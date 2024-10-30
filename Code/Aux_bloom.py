import os
from pybloom_live import BloomFilter

# Path to the Auxiliary folder
auxiliary_path = r"C:\Users\WINDOWS\Documents\CSS453_SEiMCS\Auxiliary"

# Initialize a dictionary to hold Bloom Filters for each file
branch_filters = {}

# Populate Bloom Filters for each branch file in the Auxiliary folder
for filename in os.listdir(auxiliary_path):
    if filename.endswith("_Aux_Index.txt"):
        branch_name = filename.replace("_Aux_Index.txt", "")
        file_path = os.path.join(auxiliary_path, filename)
        
        # Initialize a Bloom Filter for the branch
        bloom_filter = BloomFilter(capacity=1000, error_rate=0.001)
        
        # Populate the Bloom Filter with keywords from the file
        with open(file_path, 'r') as file:
            for line in file:
                if ':' in line:
                    keyword = line.split(':')[0].strip()
                    bloom_filter.add(keyword)
        
        # Store the Bloom Filter for the branch
        branch_filters[branch_name] = {
            "filter": bloom_filter,
            "file_path": file_path
        }

def search_keyword(keyword):
    results = {}
    for branch_name, branch in branch_filters.items():
        # Use Bloom Filter to check if the keyword might be in the branch
        if keyword in branch["filter"]:
            # Open the file only if the Bloom Filter indicates a potential match
            with open(branch["file_path"], 'r') as file:
                in_keyword_section = False
                for line in file:
                    # Check for the section header matching the keyword (e.g., "Female:")
                    if line.startswith(f"{keyword}:"):
                        in_keyword_section = True
                    elif in_keyword_section:
                        # Parse the line as a comma-separated list of PIDs
                        pids = line.strip().split(", ")
                        results[branch_name] = pids
                        break  # Stop reading the file once the keyword section is found
    return results

# Example usage: Searching for "Michael Smith" should return {'Name': ['']}
search_results = search_keyword("Michael Smith")
print(search_results)
