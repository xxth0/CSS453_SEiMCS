import hashlib
# Let's open both files and link PIDs to CIDs.

# File paths
pid_file_path = 'CTT.txt'
cid_file_path = 'Enc_MDs_CIDs.txt'
output_file_path = 'PID_to_CID.txt'

# Read the PIDs from the CTT.txt file
with open(pid_file_path, 'r') as pid_file:
    pid_lines = pid_file.readlines()

# Read the CIDs from the Enc_MDs_CIDs.txt file
with open(cid_file_path, 'r') as cid_file:
    cid_lines = cid_file.readlines()

# Prepare the mapping from PID to CID
pid_to_cid = {}

# We will assume that the lines in CTT.txt and Enc_MDs_CIDs.txt are in order
for pid_line, cid_line in zip(pid_lines, cid_lines):
    pid_parts = pid_line.strip().split(" - ")
    cid_parts = cid_line.strip().split(" ")
    
    if len(pid_parts) == 2 and len(cid_parts) == 2:
        pid_to_cid[pid_parts[0]] = cid_parts[0]  # Map PID to CID

# Now we write the resulting mapping to PID_to_CID.txt
with open(output_file_path, 'w') as output_file:
    for pid, cid in pid_to_cid.items():
        output_file.write(f"{pid} - {cid}\n")

print(f"PID to CID mapping has been written to {output_file_path}")
