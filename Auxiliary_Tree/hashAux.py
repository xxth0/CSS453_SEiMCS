import hashlib
import json

# Function to hash PIDs using SHA-256
def hash_pid(pid):
    return hashlib.sha256(pid.strip().encode()).hexdigest()

# Function to process the text data from the file
def process_text_file(file_path):
    data = {}
    with open(file_path, "r") as file:
        for line in file:
            if ":" in line:  # Detect category lines
                label, raw_pids = line.split(":")
                raw_pids = raw_pids.strip().split(",")  # Split PIDs by commas
                hashed_pids = [hash_pid(pid.strip()) for pid in raw_pids]  # Hash all PIDs
                data[label.strip()] = {
                    "raw_pids": raw_pids,
                    "hashed_pids": hashed_pids
                }
    return data

# File path to the input text file
input_file_path = "Gender_Aux_Index.txt"

# Process the file
hashed_data = process_text_file(input_file_path)

# Save the processed data to a JSON file
output_file_path = "hashed_pids.json"
with open(output_file_path, "w") as f:
    json.dump(hashed_data, f, indent=4)

print(f"Processed and hashed data saved to {output_file_path}")

