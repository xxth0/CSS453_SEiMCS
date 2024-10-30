from Crypto.Cipher import AES
import hashlib
import os

# Function to hash the key to 16 bytes using MD5
def get_aes_key(user_key):
    return hashlib.md5(user_key.encode('utf-8')).digest()

# Padding function (PKCS7) for AES block size (16 bytes)
def pad_data(data):
    padding_len = AES.block_size - len(data) % AES.block_size
    return data + bytes([padding_len] * padding_len)

# Unpadding function for PKCS7 padding
def unpad_data(data):
    padding_len = data[-1]
    return data[:-padding_len]

# Encrypt function
def encrypt_file(input_file_path, output_file_path, key):
    # Create the AES cipher in ECB mode
    cipher = AES.new(key, AES.MODE_ECB)
    
    # Read the original file data
    with open(input_file_path, 'rb') as f:
        file_data = f.read()
    
    # Pad the data and encrypt
    padded_data = pad_data(file_data)
    encrypted_data = cipher.encrypt(padded_data)
    
    # Write the encrypted data to a new file
    with open(output_file_path, 'wb') as ef:
        ef.write(encrypted_data)
    print(f"File encrypted and saved to: {output_file_path}")

# Decrypt function
def decrypt_file(input_file_path, output_file_path, key):
    # Create the AES cipher in ECB mode
    cipher = AES.new(key, AES.MODE_ECB)
    
    # Read the encrypted file data
    with open(input_file_path, 'rb') as f:
        encrypted_data = f.read()
    
    # Decrypt and unpad the data
    decrypted_data = unpad_data(cipher.decrypt(encrypted_data))
    
    # Write the decrypted data to a new file
    with open(output_file_path, 'wb') as df:
        df.write(decrypted_data)
    print(f"File decrypted and saved to: {output_file_path}")

# Example usage:
user_key = '11111111111'
aes_key = get_aes_key(user_key)

# Paths for testing
input_file = 'path/to/your/input_file.dat'
# Put the directory of the encrypted file here
encrypted_file = 'C:\\Users\\WINDOWS\\Documents\\CSS453_SEiMCS\\Enc_MDs\\0BB3B02B6FBB4BC9925C47267A44C5C3.dat'
# Put the output path and the name of the file here
decrypted_file = 'C:\\Users\\WINDOWS\\Documents\\CSS453_SEiMCS\\decrypted_file.dat'

# Encrypt the file
# encrypt_file(input_file, encrypted_file, aes_key)

# Decrypt the file
decrypt_file(encrypted_file, decrypted_file, aes_key)
