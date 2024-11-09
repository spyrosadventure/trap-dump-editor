import sys
from Crypto.Cipher import AES
import hashlib

def decrypt_skylander(sky_data):
    actikey = bytes([0x20, 0x43, 0x6F, 0x70, 0x79, 0x72, 0x69, 0x67, 0x68, 0x74, 0x20, 0x28, 0x43, 0x29, 0x20, 0x32,
                     0x30, 0x31, 0x30, 0x20, 0x41, 0x63, 0x74, 0x69, 0x76, 0x69, 0x73, 0x69, 0x6F, 0x6E, 0x2E, 0x20,
                     0x41, 0x6C, 0x6C, 0x20, 0x52, 0x69, 0x67, 0x68, 0x74, 0x73, 0x20, 0x52, 0x65, 0x73, 0x65, 0x72,
                     0x76, 0x65, 0x64, 0x2E, 0x20])
    key_input = bytearray(85)
    dec_sky = bytearray(1024)
    enc_data = bytearray(16)
    dec_data = bytearray(16)
    key = bytearray(16)
    
    h = 0
    key_input[:32] = sky_data[:32]
    key_input[33:33 + 53] = actikey[:53]

    while h <= 63:
        if ((h - 3) % 4 == 0) or h < 8 or h == 34 or h == 62:
            dec_sky[h * 16:(h + 1) * 16] = sky_data[h * 16:(h + 1) * 16]
        else:
            key_input[32] = h
            enc_data = sky_data[16 * h:16 * h + 16]
            key = calculate_md5_hash(key_input)
            dec_data = aes_decrypt(enc_data, key)
            dec_sky[h * 16:(h + 1) * 16] = dec_data[:16]
        h += 1

    return bytes(dec_sky)

def calculate_md5_hash(input_bytes):
    md5 = hashlib.md5()
    md5.update(input_bytes)
    return md5.digest()

def aes_decrypt(input_bytes, key_bytes):
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    decrypted = cipher.decrypt(input_bytes)
    return decrypted

if len(sys.argv) != 2:
    print("Usage: Drag and drop the .sky file onto this script.")
    sys.exit(1)

file_path = sys.argv[1]

with open(file_path, 'rb') as file:
    skylander_data = file.read()

decrypted_data = decrypt_skylander(skylander_data)

output_file_path = file_path.replace(".sky", ".decrypted.sky")
with open(output_file_path, 'wb') as file:
    file.write(decrypted_data)

print(f"File decrypted successfully and saved as {output_file_path}")
