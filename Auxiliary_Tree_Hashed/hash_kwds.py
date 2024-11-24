import hashlib

# Function to hash a keyword
def hash_keyword(keyword):
    return hashlib.sha256(keyword.encode()).hexdigest()

# Input and output file paths
input_file_path = "Region_Aux_Index.txt"
output_file_path = "Hashed_Region_Aux_Index.txt"

# Process the input file
with open(input_file_path, "r") as input_file, open(output_file_path, "w") as output_file:
    for line in input_file:
        if ":" in line:
            # Process the line with a keyword
            keyword, values = line.split(":", 1)
            hashed_keyword = hash_keyword(keyword.strip())
            output_file.write(f"{hashed_keyword}:{values}")
        else:
            # Write non-keyword lines as is
            output_file.write(line)

print(f"Hashed keywords written to {output_file_path}")
