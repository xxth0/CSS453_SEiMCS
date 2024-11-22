from flask import Flask, request, render_template
from web3 import Web3

# Initialize Flask app
app = Flask(__name__)

# Connect to Ganache Blockchain
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Check blockchain connection
if not web3.is_connected():
    raise Exception("Unable to connect to the blockchain!")

# Contract details
contract_address = "0x381D56f0Ee8e1d78CB32cDd2163AE8080eCDeC98"  # Replace with your contract address
abi = [
    {
        "inputs": [
            {"internalType": "string", "name": "_cid", "type": "string"},
            {"internalType": "string", "name": "_filePath", "type": "string"},
        ],
        "name": "storeFile",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "_fileId", "type": "uint256"},
        ],
        "name": "getFile",
        "outputs": [
            {"internalType": "string", "name": "", "type": "string"},
            {"internalType": "string", "name": "", "type": "string"},
            {"internalType": "address", "name": "", "type": "address"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]

# Load the smart contract
contract = web3.eth.contract(address=contract_address, abi=abi)

# Homepage
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    # Get the search keyword from the form
    keyword = request.form['keyword']

    # Perform the local search for Patient IDs
    patient_ids = search_local_patient_ids(keyword)

    # Retrieve corresponding CIDs for the Patient IDs from the blockchain
    cid_results = {}
    for patient_id in patient_ids:
        cid_results[patient_id] = retrieve_cid_from_blockchain(patient_id)

    # Render the results page with Patient IDs and corresponding CIDs
    return render_template('results.html', keyword=keyword, results=cid_results)

def search_local_patient_ids(keyword):
    """Search for Patient IDs locally based on the given keyword."""
    # Example logic to search for Patient IDs in a local database or file
    # Replace this with your actual search implementation
    patient_ids = []
    with open("indexes.txt", "r") as file:
        for line in file:
            if keyword.lower() in line.lower():
                # Assuming the line format includes Patient ID
                parts = line.strip().split()
                patient_ids.append(parts[0])  # Replace with actual Patient ID extraction
    return patient_ids

def retrieve_cid_from_blockchain(patient_id):
    """Retrieve the CID for a given Patient ID from the blockchain."""
    file_count = contract.functions.fileCount().call()  # Get total number of files
    for file_id in range(file_count):
        cid, file_path, uploader = contract.functions.getFile(file_id).call()
        if patient_id in file_path:  # Match the Patient ID with the file path
            return cid
    return None  # Return None if no CID is found


if __name__ == '__main__':
    app.run(debug=True)
