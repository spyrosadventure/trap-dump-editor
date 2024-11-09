import os
import crcmod
from trinket_tags import trinket_tags
from hat_tags import hat_tags
from villain_tags import villain_tags

crc16_ccitt_false = crcmod.predefined.mkCrcFun('crc-ccitt-false')

evolved_values = {
    1: "True",
    0: "False"
}

def write_checksum(file_path, offset, checksum_value):
    with open(file_path, 'r+b') as file:

        swapped_checksum = checksum_value.to_bytes(2, byteorder='little')
        file.seek(offset)
        file.write(swapped_checksum)
        print(f"Written Checksum {checksum_value:04X} at offset 0x{offset:X}")

def calculate_checksum_8E(data):
    checksum_data = data[0x80:0x8E]
    checksum_data += bytes([0x05, 0x00])
    print(f"Checksum Data: {checksum_data.hex()}")
    calculated_checksum = crc16_ccitt_false(checksum_data)
    print(f"Byte-swapped CRC result: {calculated_checksum:04X}")
    return calculated_checksum

def calculate_checksum_0x8C(data):
    valid_blocks = [0x90, 0xA0, 0xC0]
    checksum_data = bytearray()

    for block_start in valid_blocks:
        checksum_data.extend(data[block_start:block_start + 16])  

    calculated_checksum = crc16_ccitt_false(checksum_data)
    return calculated_checksum

def calculate_checksum_0x24C(data):
    valid_blocks = [0x250, 0x260, 0x280]
    checksum_data = bytearray()

    for block_start in valid_blocks:
        checksum_data.extend(data[block_start:block_start + 16])  

    calculated_checksum = crc16_ccitt_false(checksum_data)
    return calculated_checksum

def verify_and_update_checksums(file_path):
    consecutive_matches = {0x8E: 0, 0x8C: 0, 0x24C: 0}
    max_consecutive_matches = 3
    while True:
        with open(file_path, 'rb') as file:
            data = file.read()

            stored_checksum_8E = int.from_bytes(data[0x8E:0x90], byteorder='little')
            calculated_checksum_8E = calculate_checksum_8E(data)
            print(f"OG Checksum at 0x8E: {stored_checksum_8E:04X}, Calculated Checksum: {calculated_checksum_8E:04X}")
            if stored_checksum_8E != calculated_checksum_8E:
                write_checksum(file_path, 0x8E, calculated_checksum_8E)
                consecutive_matches[0x8E] = 0
            else:
                consecutive_matches[0x8E] += 1

            stored_checksum_8C = int.from_bytes(data[0x8C:0x8E], byteorder='little')
            calculated_checksum_8C = calculate_checksum_0x8C(data)
            print(f"OG Checksum at 0x8C: {stored_checksum_8C:04X}, Calculated Checksum: {calculated_checksum_8C:04X}")
            if stored_checksum_8C != calculated_checksum_8C:
                write_checksum(file_path, 0x8C, calculated_checksum_8C)
                consecutive_matches[0x8C] = 0
            else:
                consecutive_matches[0x8C] += 1

            stored_checksum_24C = int.from_bytes(data[0x24C:0x24E], byteorder='little')
            calculated_checksum_24C = calculate_checksum_0x24C(data)
            print(f"OG Checksum at 0x24C: {stored_checksum_24C:04X}, Calculated Checksum: {calculated_checksum_24C:04X}")
            if stored_checksum_24C != calculated_checksum_24C:
                write_checksum(file_path, 0x24C, calculated_checksum_24C)
                consecutive_matches[0x24C] = 0
            else:
                consecutive_matches[0x24C] += 1

        if all(match >= max_consecutive_matches for match in consecutive_matches.values()):
            print("All checksums match three times in a row!")
            print("use encrypt.py to encrypt your new skylander dump.")
            break  

def update_villain_id(file_path, villain_index, new_villain_id):
    if not (1 <= new_villain_id <= 46):
        print("Invalid villain ID. Please enter a value between 1 and 46.")
        return

    start_offset = 0x90
    step = 0x40
    offset = start_offset + villain_index * step

    with open(file_path, 'r+b') as file:
        file.seek(offset)

        file.write(new_villain_id.to_bytes(1, byteorder='little'))
        print(f"Updated Villain ID at 0x{offset:X} to {new_villain_id}.")

    verify_and_update_checksums(file_path)

def read_villain_data(file_path, start_offset=0x90, step=0x40, count=6):
    try:
        with open(file_path, 'rb') as file:
            data = file.read()

            verify_and_update_checksums(file_path)  
            for i in range(count):
                offset = start_offset + i * step
                file.seek(offset)

                byte_value = file.read(1)
                if not byte_value:
                    print(f"Reached end of file at offset 0x{offset:X}.")
                    break
                tag_id = int.from_bytes(byte_value, byteorder='little')

                evolved_byte = file.read(1)
                evolved_status = int.from_bytes(evolved_byte, byteorder='little')

                hat_byte = file.read(1)
                hat_value = int.from_bytes(hat_byte, byteorder='little') - 1

                trinket_byte = file.read(1)
                trinket_value = int(int.from_bytes(trinket_byte, byteorder='little'))

                villain_name = villain_tags.get(tag_id, "Unknown Tag ID")
                evolved_value = evolved_values.get(evolved_status, "Invalid Value")
                hat_name = hat_tags.get(hat_value, "Unknown Hat")
                trinket_name = trinket_tags.get(trinket_value, "Unknown Trinket")

                print(i)
                print(f"Villain ID at 0x{offset:X}: {tag_id} - {villain_name}")
                print(f"  Evolved Status: {evolved_value}")
                print(f"  Hat Value: {hat_name}")
                print(f"  Trinket Value: {trinket_name}")

    except FileNotFoundError:
        print("File not found. Please check the file path.")
    except Exception as e:
        print(f"An error occurred: {e}")

def user_input_and_update(file_path):

    file_path = file_path.strip('"')

    villain_index = int(input("Enter villain index (0-5): "))
    new_villain_id = int(0)
    update_villain_id(file_path, villain_index, new_villain_id)

print("use decrypt.py to decrypt your skylander dump.")
file_path = input("Enter the path to the decrypted dump. (drag and drop the file here): ")
user_input_and_update(file_path)
