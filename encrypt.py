import sys
from Crypto.Cipher import AES
import hashlib

def encrypt_skylander(sky_data):
    actikey = bytes([0x20, 0x43, 0x6F, 0x70, 0x79, 0x72, 0x69, 0x67, 0x68, 0x74, 0x20, 0x28, 0x43, 0x29, 0x20, 0x32,
                     0x30, 0x31, 0x30, 0x20, 0x41, 0x63, 0x74, 0x69, 0x76, 0x69, 0x73, 0x69, 0x6F, 0x6E, 0x2E, 0x20,
                     0x41, 0x6C, 0x6C, 0x20, 0x52, 0x69, 0x67, 0x68, 0x74, 0x73, 0x20, 0x52, 0x65, 0x73, 0x65, 0x72,
                     0x76, 0x65, 0x64, 0x2E, 0x20])
    key_input = bytearray(85)
    enc_sky = bytearray(1024)
    enc_data = bytearray(16)
    dec_data = bytearray(16)
    key = bytearray(16)
    
    h = 0
    key_input[:32] = sky_data[:32]
    key_input[33:33 + 53] = actikey[:53]

    while h <= 63:
        if ((h - 3) % 4 == 0) or h < 8 or h == 34 or h == 62:
            enc_sky[h * 16:(h + 1) * 16] = sky_data[h * 16:(h + 1) * 16]
        else:
            key_input[32] = h
            dec_data = sky_data[16 * h:16 * h + 16]
            key = calculate_md5_hash(key_input)
            enc_data = aes_encrypt(dec_data, key)
            enc_sky[h * 16:(h + 1) * 16] = enc_data[:16]
        h += 1

    return bytes(enc_sky)

def calculate_md5_hash(input_bytes):
    md5 = hashlib.md5()
    md5.update(input_bytes)
    return md5.digest()

def aes_encrypt(input_bytes, key_bytes):
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    encrypted = cipher.encrypt(input_bytes)
    return encrypted

if len(sys.argv) != 2:
    print("Usage: Drag and drop the .sky file onto this script.")
    sys.exit(1)

file_path = sys.argv[1]  # The file path is passed as the first argument

with open(file_path, 'rb') as file:
    skylander_data = file.read()

encrypted_data = encrypt_skylander(skylander_data)

output_file_path = file_path.replace(".sky", ".Encrypted.sky")
with open(output_file_path, 'wb') as file:
    file.write(encrypted_data)

print(f"File encrypted successfully and saved as {output_file_path}")
