from web3 import Web3
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables
ganache_url = os.getenv("GANACHE_URL")
auth_contract_address = os.getenv("AUTH_CONTRACT_ADDRESS")
auth_abi_file_path = os.getenv("AUTH_ABI_FILE_PATH")
private_key = os.getenv("PRIVATE_KEY")
user_address = Web3.to_checksum_address(os.getenv("USER_ADDRESS"))
default_password = os.getenv("DEFAULT_PASSWORD")

# Connect to Ganache
Web3 = Web3(Web3.HTTPProvider(ganache_url))

if not Web3.is_connected():
    raise Exception("Failed to connect to Ganache")
print("Connected to Blockchain")

# Load ABI
try:
    with open(auth_abi_file_path, "r") as abi_file:
        auth_contract_abi = json.load(abi_file)["abi"]
except FileNotFoundError:
    raise Exception(f"ABI file not found at {auth_abi_file_path}")

auth_contract = Web3.eth.contract(address=auth_contract_address, abi=auth_contract_abi)

# Hash Password
def hash_password(password):
    return Web3.solidity_keccak(['string'], [password])

# Register User
try:
    password_hash = hash_password(default_password)

    print(f"Registering user: {user_address}")
    print(f"Generated Password Hash: {password_hash}")

    # Build the transaction (without role)
    txn = auth_contract.functions.registerUser(user_address, password_hash).build_transaction({
        'from': Web3.eth.accounts[0],
        'gas': 3000000,
        'nonce': Web3.eth.get_transaction_count(Web3.eth.accounts[0]),
    })

    # Sign and send the transaction
    signed_txn = Web3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_hash = Web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    receipt = Web3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"Transaction Hash: {tx_hash.hex()}")
    print(f"Transaction Receipt: {receipt}")

    # Verify the stored hash
    stored_hash = auth_contract.functions.getStoredHash(user_address).call()
    print(f"Stored Password Hash: {stored_hash}")

    if stored_hash == password_hash:
        print("User registered successfully.")
    else:
        print("Warning: Hash mismatch! Registration may have failed.")

except Exception as e:
    print(f"Error during registration: {e}")
