import os
from pybloom_live import BloomFilter

# Paths for auxiliary and tree data folders
auxiliary_path = r"C:\Users\WINDOWS\Documents\CSS453_SEiMCS\Auxiliary_Tree"
tree_path = r"C:\Users\WINDOWS\Documents\CSS453_SEiMCS\Tree_Data"

# Initialize dictionaries to hold Bloom Filters for each file
aux_branch_filters = {}
tree_branch_filters = {}

# Helper function to count lines that have the character ':'
def get_line_count(file_path):
    with open(file_path, 'r') as file:
        return sum(1 for line in file if ':' in line)

# Populate Bloom Filters for each branch file in the Auxiliary folder
def populate_auxiliary_filters():
    for filename in os.listdir(auxiliary_path):
        if filename.endswith("_Aux_Index.txt"):
            branch_name = filename.replace("_Aux_Index.txt", "")
            file_path = os.path.join(auxiliary_path, filename)

            # Determine capacity dynamically and add a buffer to avoid capacity issues
            estimated_capacity = get_line_count(file_path) * 2

            # Initialize a Bloom Filter for the branch
            bloom_filter = BloomFilter(capacity=estimated_capacity, error_rate=0.001)

            # Populate the Bloom Filter with keywords from the file
            with open(file_path, 'r') as file:
                for line in file:
                    if ':' in line:
                        keyword = line.split(':')[0].strip()
                        bloom_filter.add(keyword)

            # Store the Bloom Filter for the branch
            aux_branch_filters[branch_name] = {
                "filter": bloom_filter,
                "file_path": file_path
            }

# Populate Bloom Filters for each branch file in the Tree folder
def populate_tree_filters():
    for filename in os.listdir(tree_path):
        if filename.endswith("_Index.txt"):
            branch_name = filename.replace("_Index.txt", "")
            file_path = os.path.join(tree_path, filename)

            # Determine capacity dynamically and add a buffer to avoid capacity issues
            estimated_capacity = get_line_count(file_path) * 2

            # Initialize a Bloom Filter for the branch
            bloom_filter = BloomFilter(capacity=estimated_capacity, error_rate=0.001)

            # Populate the Bloom Filter with keywords from the file
            with open(file_path, 'r') as file:
                for line in file:
                    if ':' in line:
                        keyword = line.split(':')[0].strip()
                        bloom_filter.add(keyword)

            # Store the Bloom Filter for the branch
            tree_branch_filters[branch_name] = {
                "filter": bloom_filter,
                "file_path": file_path
            }

# Function to search for keywords using Auxiliary Bloom filters
def search_auxiliary_keyword(keyword):
    results = {}
    for branch_name, branch in aux_branch_filters.items():
        # Use Bloom Filter to check if the keyword might be in the branch
        if keyword in branch["filter"]:
            # Open the file only if the Bloom Filter indicates a potential match
            with open(branch["file_path"], 'r') as file:
                in_keyword_section = False
                for line in file:
                    if line.startswith(f"{keyword}:"):
                        in_keyword_section = True
                    elif in_keyword_section:
                        # Parse the line as a comma-separated list of PIDs
                        pids = line.strip().split(", ")
                        results[branch_name] = pids
                        break
    return results

# Function to search for keywords using Tree Bloom filters
def search_tree_keyword(keyword):
    results = {}
    for branch_name, branch in tree_branch_filters.items():
        # Use Bloom Filter to check if the keyword might be in the branch
        if keyword in branch["filter"]:
            # Open the file only if the Bloom Filter indicates a potential match
            with open(branch["file_path"], 'r') as file:
                in_keyword_section = False
                for line in file:
                    if line.startswith(f"{keyword}:"):
                        in_keyword_section = True
                    elif in_keyword_section:
                        # Parse the line as a comma-separated list of PIDs
                        pids = line.strip().split(", ")
                        results[branch_name] = pids
                        break
    return results

# Function to search for a keyword in both auxiliary and tree datasets
def search_combined(keyword):
    aux_results = search_auxiliary_keyword(keyword)
    tree_results = search_tree_keyword(keyword)

    # Combine results from both searches
    combined_results = {
        "Auxiliary Results": aux_results,
        "Tree Results": tree_results
    }

    return combined_results

# Main Execution
if __name__ == "__main__":
    # Populate Bloom Filters for both Auxiliary and Tree folders
    populate_auxiliary_filters()
    populate_tree_filters()

    # Example usage: Searching for a keyword across both datasets
    keyword = "Latex"
    combined_search_results = search_combined(keyword)
    print("Combined Search Results:")
    print(combined_search_results)
