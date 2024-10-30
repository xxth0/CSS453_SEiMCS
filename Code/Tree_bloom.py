import os

# Path to CTT.txt
ctt_file_path = r"C:\Users\WINDOWS\Documents\CSS453_SEiMCS\Tree\CTT.txt"

# Function to retrieve CTT files based on PIDs
def find_ctt_files(pids):
    ctt_results = {}
    with open(ctt_file_path, 'r') as file:
        for line in file:
            pid, ctt_filename = line.strip().split(" - ")
            pid = int(pid)
            if pid in pids:
                ctt_results[pid] = ctt_filename
    return ctt_results

# Example usage with a list of PIDs (replace with actual PIDs from the auxiliary index search)
example_pids = [1, 4, 5, 10, 475]  # Replace with PIDs you are searching for
ctt_files = find_ctt_files(example_pids)

# Output the results
print("CTT Files Found:")
for pid, ctt_file in ctt_files.items():
    print(f"PID: {pid}, CTT File: {ctt_file}")
