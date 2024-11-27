import os
from pybloom_live import BloomFilter
import pickle

# Define the path to auxiliary files and the output directory for Bloom filters
auxiliary_path = "C:/Users/WINDOWS/Documents/CSS453_SEiMCS/Auxiliary_Tree_Hashed"
bloom_output_path = "C:/Users/WINDOWS/Documents/CSS453_SEiMCS/Bloom_Filters"
os.makedirs(bloom_output_path, exist_ok=True)

# Iterate over auxiliary files to create Bloom filters
for filename in os.listdir(auxiliary_path):
    if filename.endswith(".txt"):
        filepath = os.path.join(auxiliary_path, filename)
        bloom_filename = os.path.splitext(filename)[0] + ".bloom"
        bloom_filepath = os.path.join(bloom_output_path, bloom_filename)

        # Create a Bloom filter with an estimated capacity
        bloom_filter = BloomFilter(capacity=10000, error_rate=0.001)

        with open(filepath, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if ':' in line:  # Skip PIDs or irrelevant lines
                    hashed_keyword = line.split(':')[0].strip()  # Use the hashed keyword directly
                    bloom_filter.add(hashed_keyword)
                    print(f"Added hashed keyword '{hashed_keyword}' to Bloom filter")

        # Save the Bloom filter
        with open(bloom_filepath, 'wb') as bloom_file:
            pickle.dump(bloom_filter, bloom_file)

        print(f"Created Bloom filter for {filename} at {bloom_filepath}")
