from flask import Flask, request, render_template, flash
from fuzzywuzzy import fuzz
import os
import hashlib
from web3 import Web3
import json
from time import time

app = Flask(__name__)

# Connect to Ganache
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

if not web3.is_connected():
    raise Exception("Failed to connect to Ganache")
print("Connected to Blockchain")

# Contract Details
contract_address = "0xB48A780AE836f7664Ed7Dc4842b5E1CdB2B1EF2A"
abi_file_path = r"C:\Users\WINDOWS\Documents\CSS453_SEiMCS\build\contracts\StoreCIDs.json"

# Load ABI
with open(abi_file_path, "r") as abi_file:
    contract_abi = json.load(abi_file)["abi"]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Path to auxiliary indexes
auxiliary_path = "C:/Users/WINDOWS/Documents/CSS453_SEiMCS/Auxiliary_Tree"

# Function to hash PID
def hash_pid(pid):
    return hashlib.sha256(pid.encode()).hexdigest()

# Function to retrieve CID for a hashed PID
def get_cid(hashed_pid):
    try:
        return contract.functions.getCID(hashed_pid).call()
    except Exception as e:
        print(f"Error querying CID for hashed PID: {hashed_pid} -> {e}")
        return None

 # One of the operation requirement (Search in Range)
def search_pids_in_range(start, end):
    """Search for PIDs within a specific range."""
    range_pids = [str(pid) for pid in range(int(start), int(end) + 1)]
    return range_pids


def search_auxiliary(keywords):
    results = None  # Initialize as None to compute intersection
    for filename in os.listdir(auxiliary_path):
        if filename.endswith("_Aux_Index.txt"):
            with open(os.path.join(auxiliary_path, filename), 'r') as file:
                lines = file.readlines()
                for keyword in keywords:
                    for i, line in enumerate(lines):
                        if fuzz.partial_ratio(keyword.lower(), line.strip().lower()) > 80:  # Adjust threshold as needed
                            pids = set(lines[i + 1].strip().split(", "))
                            if results is None:
                                results = pids  # Initialize the intersection set
                            else:
                                results &= pids  # Intersect with existing results
                            break
    return results or set()  # Return an empty set if no matches are found

@app.route('/')
def home():
    return render_template('index.html')

from flask import Flask, request, render_template, flash

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    inputs = query.split(",")
    inputs = [item.strip() for item in inputs]

    # Validate inputs
    if not query.strip():
        flash("Search query cannot be empty. Please provide a valid keyword or PID.", "error")
        return render_template('index.html')

    if all(not item.isnumeric() and len(item) < 3 for item in inputs):
        flash("Please enter valid keywords (at least 3 characters) or numeric PIDs.", "error")
        return render_template('index.html')

    start_time = time()

    keyword_results = {"cids": {}}
    pid_results = {}
    intersection_pids = set()  # To store intersected results

    # Process inputs as PIDs and keywords
    for input_item in inputs:
        # Range Search
        if '-' in input_item and all(part.isdigit() for part in input_item.split('-')):
            start, end = map(int, input_item.split('-'))
            range_pids = set(search_pids_in_range(start, end))
            if not intersection_pids:
                intersection_pids = range_pids
            else:
                intersection_pids &= range_pids
            continue

        # NOT Operation
        elif input_item.startswith('NOT:'):
            not_keyword = input_item.replace('NOT:', '').strip()
            excluded_pids = set(search_auxiliary([not_keyword]))
            if intersection_pids:
                intersection_pids -= excluded_pids
            continue

        # OR Operation
        elif input_item.startswith('OR:'):
            or_keywords = input_item.replace('OR:', '').split('|')
            or_results = set()
            for keyword in or_keywords:
                or_results |= set(search_auxiliary([keyword.strip()]))
            if not intersection_pids:
                intersection_pids = or_results
            else:
                intersection_pids |= or_results
            continue

        # PID Search
        elif input_item.isnumeric():
            hashed_pid = hash_pid(input_item)
            cid = get_cid(hashed_pid)
            pid_results[input_item] = {"hashed_pid": hashed_pid, "cid": cid}
            continue

        # Default: Keyword Search
        else:
            matching_pids = set(search_auxiliary([input_item]))
            if not intersection_pids:
                intersection_pids = matching_pids
            else:
                intersection_pids &= matching_pids

    # Hash PIDs from the keyword intersection and query blockchain
    # Sort PIDs before returning results
    if intersection_pids:
        sorted_pids = sorted(intersection_pids, key=int)  # Sort numerically
        hashed_pids = [hash_pid(pid) for pid in sorted_pids]
        keyword_results["cids"] = {
            pid: get_cid(hpid) for pid, hpid in zip(sorted_pids, hashed_pids)
        }


    end_time = time()

    return render_template(
        'results.html',
        keywords=query,
        pid_results=pid_results,
        keyword_results=keyword_results,
        search_time=round(end_time - start_time, 4),
        hash_pid=hash_pid
    )




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

