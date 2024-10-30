import os
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Set paths for the directories and output file
enc_extract_path = '/mnt/data/Enc_MDs/'  # Folder containing encrypted .dat files
output_file_path = '/mnt/data/PID_Filename_List.txt'

# Function to get AES key from the provided key string
def get_aes_key(user_key):
    return hashlib.md5(user_key.encode('utf-8')).digest()

# Decryption function based on AES ECB mode with PKCS7 padding
def decrypt_data(encrypted_data, aes_key):
    cipher = AES.new(aes_key, AES.MODE_ECB)
    decrypted_data = cipher.decrypt(encrypted_data)
    return unpad(decrypted_data, AES.block_size)

# Initialize the AES key from the provided encryption key
encryption_key = "11111111111"
aes_key = get_aes_key(encryption_key)

# Initialize list to store PID and filename mappings
pid_filename_mappings = []

# Loop through each encrypted .dat file to decrypt and extract PID
for file_name in os.listdir(enc_extract_path):
    file_path = os.path.join(enc_extract_path, file_name)
    with open(file_path, 'rb') as file:
        encrypted_data = file.read()
        try:
            # Decrypting the file content
            decrypted_content = decrypt_data(encrypted_data, aes_key).decode('utf-8', errors='ignore')
            # Extracting PID from the decrypted content by finding the "Patient ID" row
            lines = decrypted_content.splitlines()
            if lines and "Patient ID" in lines[0]:
                # Extract the PID from the decrypted content
                pid = int(lines[1].split(',')[0].strip())
                # Append to list only if PID is within the range 1 to 1000
                if 1 <= pid <= 1000:
                    pid_filename_mappings.append((pid, file_name))
        except Exception as e:
            # Log files that encounter decryption issues
            pid_filename_mappings.append((file_name, f"Decryption Error: {str(e)}"))

# Sort the mappings by PID for ordered output
pid_filename_mappings.sort()

# Format output content and write to the specified file
output_lines = [f"{pid} - {filename}" for pid, filename in pid_filename_mappings]
output_content = "\n".join(output_lines)

with open(output_file_path, 'w') as file:
    file.write(output_content)

print(f"PID-to-filename mapping saved to {output_file_path}")
