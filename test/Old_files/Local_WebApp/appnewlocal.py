import os
import hashlib
from web3 import Web3
from flask import Flask, request, render_template
from pybloom_live import BloomFilter
from time import time
import logging

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

SECRET_KEY = b"your-32-byte-key12345678901234"

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set log level to DEBUG
logger = logging.getLogger(__name__)


app = Flask(__name__)

# Connect to Ganache
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Verify blockchain connection
if web3.is_connected():
    print("Connected to Blockchain")
else:
    raise Exception("Failed to connect to Ganache")

# Contract Details
contract_address = "0x0B1Fbb3bfAbFABd7fD71d7B95FAd89B34188f2E1"  # Replace with your deployed contract address
contract_abi = [
    {
        "inputs": [
            {"internalType": "string", "name": "hashedPid", "type": "string"},
            {"internalType": "string", "name": "cid", "type": "string"}
        ],
        "name": "addMapping",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "hashedPid", "type": "string"}],
        "name": "getCID",
        "outputs": [{"internalType": "string", "name": "cid", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    }
]
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def encrypt_data(data):
    cipher = AES.new(SECRET_KEY, AES.MODE_ECB)
    encrypted = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    return base64.b64encode(encrypted).decode('utf-8')

def decrypt_data(encrypted_data):
    cipher = AES.new(SECRET_KEY, AES.MODE_ECB)
    decoded = base64.b64decode(encrypted_data)
    return unpad(cipher.decrypt(decoded), AES.block_size).decode('utf-8')

# Hashing Function for PIDs
def hash_pid(pid):
    """Hashes the PID using SHA-256."""
    return hashlib.sha256(pid.encode()).hexdigest()

# Add a mapping function
def add_mapping(pid, cid):
    """Adds a PID-CID mapping to the blockchain."""
    hashed_pid = hash_pid(pid)  # Hash the PID
    try:
        tx_hash = contract.functions.addMapping(hashed_pid, cid).transact({'from': web3.eth.accounts[0]})
        web3.eth.wait_for_transaction_receipt(tx_hash)
        logger.debug(f"[ADD_MAPPING] Original PID: {pid}, Hashed PID: {hashed_pid}, CID: {cid}")
    except Exception as e:
        print(f"Error adding mapping: {e}")

# Auxiliary Tree Directory
auxiliary_path = "C:/Users/WINDOWS/Documents/CSS453_SEiMCS/Auxiliary_Tree"

# Initialize Bloom Filters for Auxiliary Tree
bloom_filters = {}
for filename in os.listdir(auxiliary_path):
    if filename.endswith("_Aux_Index.txt"):
        branch_name = filename.replace("_Aux_Index.txt", "")
        file_path = os.path.join(auxiliary_path, filename)

        bloom_filter = BloomFilter(capacity=1000, error_rate=0.001)
        with open(file_path, 'r') as file:
            for line in file:
                if ':' in line:
                    keyword = line.split(':')[0].strip()
                    bloom_filter.add(keyword)

        bloom_filters[branch_name] = {"filter": bloom_filter, "file_path": file_path}

def search_keywords(keywords):
    keyword_results = {}
    for keyword in keywords:
        for branch, data in bloom_filters.items():
            if keyword in data["filter"]:
                with open(data["file_path"], 'r') as file:
                    lines = file.readlines()
                    for i, line in enumerate(lines):
                        if line.strip() == f"{keyword}:":  # Match keyword
                            raw_pids = set(lines[i + 1].strip().split(", "))
                            hashed_pids = {hash_pid(pid) for pid in raw_pids}  # Hash PIDs
                            if keyword not in keyword_results:
                                keyword_results[keyword] = set()
                            keyword_results[keyword].update(hashed_pids)
                            break
    return keyword_results


# Blockchain Query Function
def get_cid(pid):
    """Retrieves the CID for a single PID."""
    hashed_pid = hash_pid(pid)  # Hash the PID before querying
    try:
        cid = contract.functions.getCID(hashed_pid).call()
        print(f"Retrieved CID for PID={pid}, Hashed PID={hashed_pid}: {cid}")
        return cid
    except Exception as e:
        print(f"Error retrieving CID for PID={pid}, Hashed PID={hashed_pid}: {e}")
        return None

def get_cids_for_pids(hashed_pids):
    """Retrieves CIDs for hashed PIDs."""
    try:
        cids = contract.functions.getCIDs(list(hashed_pids)).call()
        return {hashed_pids[i]: cids[i] for i in range(len(hashed_pids))}
    except Exception as e:
        print(f"Error retrieving CIDs for hashed PIDs: {e}")
        return {hashed_pid: "Not Found" for hashed_pid in hashed_pids}


logger.debug("Flask logging test: Is this visible?")

# Write logs to a file
file_handler = logging.FileHandler("flask_debug.log")
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# Flask Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    # Parse input keywords
    keywords = request.form['keywords'].split(",")
    keywords = [k.strip() for k in keywords]

    # Start time
    start_time = time()

    # Prepare results
    results = {}
    for pid in keywords:
        hashed_pid = hash_pid(pid)  # Generate hashed PID
        cid = get_cid(pid)  # Retrieve CID
        results[pid] = {"hashed_pid": hashed_pid, "cid": cid}

    # End time
    end_time = time()

    # Display Results
    return render_template(
        'results.html',
        keywords=keywords,
        results=results,
        search_time=round(end_time - start_time, 4)
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Ensure debug=True

