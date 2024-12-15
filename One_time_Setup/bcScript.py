from web3 import Web3
import json
import hashlib
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch values from .env
ganache_url = os.getenv("GANACHE_URL")
contract_address = os.getenv("CONTRACT_ADDRESS")
abi_file_path = os.getenv("ABI_FILE_PATH")
private_key = os.getenv("PRIVATE_KEY")
file_path = os.getenv("FILE_PATH")
chain_id = int(os.getenv("CHAIN_ID", 1337))  # Default to 1337 if not provided

# Connect to Ganache blockchain
web3 = Web3(Web3.HTTPProvider(ganache_url))
if not web3.is_connected():
    raise Exception("Failed to connect to Ganache")
print("Connected to Ganache")

# Load ABI from the specified path
with open(abi_file_path, "r") as abi_file:
    contract_abi = json.load(abi_file)["abi"]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Account derived from private key
account = web3.eth.account.from_key(private_key).address
print(f"Using account: {account}")

# Hash function for PID
def hash_pid(pid):
    return hashlib.sha256(pid.encode()).hexdigest()

# Function to sign and send transactions
def send_transaction(hpid, cid):
    try:
        nonce = web3.eth.get_transaction_count(account)
        transaction = contract.functions.addMapping(hpid, cid).build_transaction({
            "chainId": chain_id,
            "gas": 2000000,
            "gasPrice": web3.to_wei("20", "gwei"),
            "nonce": nonce
        })
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transaction successful: {tx_hash.hex()}")
    except Exception as e:
        print(f"Error during transaction: {e}")
        raise

# Batch upload function
def batch_upload(file_path, batch_size=1000):
    with open(file_path, "r") as file:
        lines = file.readlines()

    success_count = 0
    for i in range(0, len(lines), batch_size):
        batch = lines[i:i + batch_size]
        for line in batch:
            try:
                hpid, cid = line.strip().split(" - ")
                send_transaction(hpid, cid)
                success_count += 1
            except Exception as e:
                print(f"Failed to upload HPID-CID pair: {line.strip()} -> {e}")
    print(f"Batch upload complete. Total successful uploads: {success_count}")

# Execute the batch upload
batch_upload(file_path)
