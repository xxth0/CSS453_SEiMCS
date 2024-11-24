from web3 import Web3
import json
import hashlib

# Connect to Ganache blockchain
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

if not web3.is_connected():
    raise Exception("Failed to connect to Ganache")
print("Connected to Ganache")

# Contract details
contract_address = "0xB48A780AE836f7664Ed7Dc4842b5E1CdB2B1EF2A"
abi_file_path = r"C:\Users\WINDOWS\Documents\CSS453_SEiMCS\build\contracts\StoreCIDs.json"

# Load ABI from the specified path
with open(abi_file_path, "r") as abi_file:
    contract_abi = json.load(abi_file)["abi"]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Private key and account derived from it
private_key = "0x3d1ca9d4054c218f4e58a7e2e8f7f5339d0ae66041c327b635a1f02dc3be21e4"
account = web3.eth.account.from_key(private_key).address
print(f"Using account: {account}")

# File containing HPIDs and CIDs
file_path = "HPIDs to CIDs.txt"

# Hash function for PID
def hash_pid(pid):
    return hashlib.sha256(pid.encode()).hexdigest()

# Function to sign and send transactions
def send_transaction(hpid, cid):
    try:
        nonce = web3.eth.get_transaction_count(account)
        transaction = contract.functions.addMapping(hpid, cid).build_transaction({
            "chainId": 1337,  # Ganache's default chain ID
            "gas": 2000000,
            "gasPrice": web3.to_wei("20", "gwei"),
            "nonce": nonce
        })
        # Sign the transaction
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        print(f"Signed transaction object: {signed_txn}")
        print(f"Available attributes: {dir(signed_txn)}")  # Debug attributes of the signed transaction

        # Access raw transaction
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
