from web3 import Web3
import json
import hashlib
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables
ganache_url = os.getenv("GANACHE_URL")
contract_address = os.getenv("CONTRACT_ADDRESS")
abi_file_path = os.getenv("ABI_FILE_PATH")
private_key = os.getenv("PRIVATE_KEY")
chain_id = int(os.getenv("CHAIN_ID", 1337))  # Default to 1337
pid = os.getenv("PID")
cid = os.getenv("CID")

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

# Function to sign and send the transaction
def send_transaction(hpid, cid):
    try:
        nonce = web3.eth.get_transaction_count(account)
        transaction = contract.functions.addMapping(hpid, cid).build_transaction({
            "chainId": chain_id,
            "gas": 2000000,
            "gasPrice": web3.to_wei("20", "gwei"),
            "nonce": nonce
        })

        # Sign the transaction
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

        # Send the transaction
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        print(f"Transaction successful with hash: {tx_hash.hex()}")
        print(f"Transaction receipt: {receipt}")
    except Exception as e:
        print(f"Error during transaction: {e}")
        raise

# Upload PID and CID from .env
hpid = hash_pid(pid)
print(f"Uploading PID: {pid}, HPID: {hpid}, CID: {cid}")
send_transaction(hpid, cid)
