import os
import csv  # Import to handle CSV parsing
import hashlib
import shutil  # To delete temporary folders
from web3 import Web3
from flask import Flask, request, render_template, send_from_directory
from Crypto.Cipher import AES
from pybloom_live import BloomFilter
from time import time  # Import the time module

app = Flask(__name__)

# Initialize blockchain connection
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))
contract_address = "0x381D56f0Ee8e1d78CB32cDd2163AE8080eCDeC98"  # Replace with your contract address
abi = [
    {
        "inputs": [{"internalType": "uint256", "name": "_fileId", "type": "uint256"}],
        "name": "getFile",
        "outputs": [
            {"internalType": "string", "name": "", "type": "string"},  # CID
            {"internalType": "string", "name": "", "type": "string"},  # File Path
            {"internalType": "address", "name": "", "type": "address"},  # Uploader
        ],
        "stateMutability": "view",
        "type": "function",
    }
]
contract = web3.eth.contract(address=contract_address, abi=abi)

# Path to Auxiliary_Tree directory
auxiliary_path = r"C:/Users/WINDOWS/Documents/CSS453_SEiMCS/Auxiliary_Tree"

# Path to the Enc_MDs directory
enc_mds_path = r"C:/Users/WINDOWS/Documents/CSS453_SEiMCS/Enc_MDs"

decrypted_output_path = r"C:/Users/WINDOWS/Documents/CSS453_SEiMCS/Decrypted_Files"

# AES Helper Functions
def get_aes_key(user_key):
    return hashlib.md5(user_key.encode('utf-8')).digest()

def pad_data(data):
    padding_len = AES.block_size - len(data) % AES.block_size
    return data + bytes([padding_len] * padding_len)

def unpad_data(data):
    padding_len = data[-1]
    return data[:-padding_len]

def retrieve_cid_from_blockchain(file_id):
    """Retrieve CID for a given file ID from the blockchain."""
    try:
        cid, file_path, uploader = contract.functions.getFile(file_id).call()
        return cid
    except Exception as e:
        print(f"Error retrieving CID for File ID {file_id}: {e}")
        return None

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

# Initialize a dictionary to hold Bloom Filters and file paths for each branch
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
        
        # Store the Bloom Filter and file path for the branch
        branch_filters[branch_name] = {
            "filter": bloom_filter,
            "file_path": file_path
        }

def search_multi_keywords(keywords):
    """Search for multiple keywords across all branches and return matching IDs."""
    results = {}
    keyword_id_sets = []  # To store sets of IDs for each keyword

    for keyword in keywords:
        keyword_results = {}
        for branch_name, branch in branch_filters.items():
            if keyword in branch["filter"]:
                with open(branch["file_path"], 'r') as file:
                    lines = file.readlines()
                    for i, line in enumerate(lines):
                        if line.strip() == f"{keyword}:":
                            ids = set(lines[i + 1].strip().split(", "))
                            keyword_results[branch_name] = ids
                            break
        all_ids = set()
        for ids in keyword_results.values():
            all_ids.update(ids)
        keyword_id_sets.append(all_ids)

    if keyword_id_sets:
        common_ids = set.intersection(*keyword_id_sets)
        results["Common"] = list(common_ids)

    return results

def search_multi_keywords_with_file_index(keywords):
    """Search for multiple keywords, retrieve matching IDs, and include file index."""
    # Load the ID-to-file mapping from CTT.txt
    file_index_path = r"C:/Users/WINDOWS/Documents/CSS453_SEiMCS/Tree/CTT.txt"
    id_to_file_map = {}
    with open(file_index_path, 'r') as file:
        for line in file:
            parts = line.strip().split(" - ")
            if len(parts) == 2:
                id_to_file_map[parts[0].strip()] = parts[1].strip()

    results = {}
    keyword_id_sets = []  # To store sets of IDs for each keyword

    for keyword in keywords:
        keyword_results = {}
        for branch_name, branch in branch_filters.items():
            if keyword in branch["filter"]:
                with open(branch["file_path"], 'r') as file:
                    lines = file.readlines()
                    for i, line in enumerate(lines):
                        if line.strip() == f"{keyword}:":
                            ids = set(lines[i + 1].strip().split(", "))
                            keyword_results[branch_name] = ids
                            break
        all_ids = set()
        for ids in keyword_results.values():
            all_ids.update(ids)
        keyword_id_sets.append(all_ids)

    if keyword_id_sets:
        common_ids = set.intersection(*keyword_id_sets)
        results["Common"] = {
            id_: id_to_file_map.get(id_, "File not found")
            for id_ in common_ids
        }

    # Include IDs and their file indices for each branch
    for keyword_result in keyword_results.items():
        branch, ids = keyword_result
        results[branch] = {
            id_: id_to_file_map.get(id_, "File not found")
            for id_ in ids
        }

    return results

def search_multi_keywords_with_file_index_and_blockchain(keywords):
    """Search for multiple keywords, retrieve matching IDs, and fetch CIDs from the blockchain."""
    results = {}
    keyword_id_sets = []  # To store sets of IDs for each keyword

    for keyword in keywords:
        keyword_results = {}
        for branch_name, branch in branch_filters.items():
            if keyword in branch["filter"]:
                with open(branch["file_path"], 'r') as file:
                    lines = file.readlines()
                    for i, line in enumerate(lines):
                        if line.strip() == f"{keyword}:":
                            ids = set(lines[i + 1].strip().split(", "))
                            keyword_results[branch_name] = ids
                            break
        all_ids = set()
        for ids in keyword_results.values():
            all_ids.update(ids)
        keyword_id_sets.append(all_ids)

    if keyword_id_sets:
        common_ids = set.intersection(*keyword_id_sets)
        results["Common"] = {
            id_: retrieve_cid_from_blockchain(int(id_))
            for id_ in common_ids
        }

    # Include IDs and their CIDs for each branch
    for keyword_result in keyword_results.items():
        branch, ids = keyword_result
        results[branch] = {
            id_: retrieve_cid_from_blockchain(int(id_))
            for id_ in ids
        }

    return results


@app.route('/')
def home():
    """Render the home page with a search form."""
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    """Handle multi-keyword search and display results."""
    keywords = request.form['keywords'].split(",")  # Split input by commas
    keywords = [k.strip() for k in keywords]  # Remove extra whitespace
    
    start_time = time()  # Record the start time
    results = search_multi_keywords_with_file_index_and_blockchain(keywords)
    end_time = time()  # Record the end time

    search_time = round(end_time - start_time, 4)  # Calculate elapsed time (in seconds)

    return render_template('resultslocal.html', keywords=keywords, results=results, search_time=search_time)


@app.route('/download/<filename>')
def download_file(filename):
    """Serve a file from the Enc_MDs directory for download."""
    return send_from_directory(enc_mds_path, filename, as_attachment=True)

@app.route('/decrypt/<filename>', methods=['GET', 'POST'])
def decrypt_and_view(filename):
    """Decrypt and display the raw medical record."""
    user_key = "11111111111"  # Replace with a secure method of obtaining the key
    aes_key = get_aes_key(user_key)

    # Create a temporary folder for decrypted files
    temp_dir = os.path.join(decrypted_output_path, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    input_file = os.path.join(enc_mds_path, filename)
    output_file = os.path.join(temp_dir, f"decrypted_{filename}.csv")
    
    try:
        # Decrypt the file
        decrypt_file(input_file, output_file, aes_key)

        # Parse the decrypted CSV file
        table_data = []
        with open(output_file, 'r') as df:
            csv_reader = csv.reader(df)
            for row in csv_reader:
                table_data.append(row)

        # Render the record
        response = render_template('view_record.html', filename=filename, table_data=table_data)

    finally:
        # Cleanup: Delete the temporary directory and its contents
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

