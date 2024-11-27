from web3 import Web3
import hashlib

# Connect to the Ganache blockchain
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Verify connection
if web3.is_connected():
    print("Connected to Ganache")
else:
    raise Exception("Failed to connect to Ganache")

# Contract address and ABI
contract_address = "0x278375D6c51366eA90880C05a7e9a9475ed6408E"  # Replace with your deployed contract address
contract_abi = [
    {
        "inputs": [
            {"internalType": "string", "name": "pid", "type": "string"},
            {"internalType": "string", "name": "cid", "type": "string"}
        ],
        "name": "addMapping",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Private key and account address
private_key = "0x126259f7770ea8c1f989a7c1fc84d7e2c6ba713cedb9c6f3fdc16842c7ef110f"
account_address = web3.eth.account.from_key(private_key).address
print(f"Using account: {account_address}")

# Connect to the deployed contract
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Hashing function for PID
def hash_pid(pid):
    """Hashes the PID using SHA-256."""
    return hashlib.sha256(pid.encode()).hexdigest()

# Load PID-CID pairs from the file
pid_cid_file = "PID_to_CID_Mapping.txt"  # Replace with your file path
with open(pid_cid_file, "r") as file:
    pid_cid_pairs = [line.strip().split(" - ") for line in file]

# Function to send transactions
def send_transaction(pid, cid):
    """Sends a transaction to the blockchain."""
    hashed_pid = hash_pid(pid)  # Hash the PID
    nonce = web3.eth.get_transaction_count(account_address)  # Correct method for getting nonce

    # Build the transaction
    transaction = contract.functions.addMapping(hashed_pid, cid).build_transaction({
        'chainId': 1337,  # Ganache's default chain ID
        'gas': 2000000,
        'gasPrice': web3.to_wei('20', 'gwei'),
        'nonce': nonce
    })

    # Sign the transaction
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

    # Send the transaction
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Transaction successful with hash: {tx_hash.hex()}")

# Batch upload
for pid, cid in pid_cid_pairs:
    try:
        print(f"Uploading PID: {pid}, CID: {cid}")
        send_transaction(pid, cid)
    except Exception as e:
        print(f"Error uploading PID {pid}: {e}")
