from web3 import Web3
import json

# Connect to Ganache
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

if not web3.is_connected():
    raise Exception("Failed to connect to Ganache")
print("Connected to Blockchain")

# Smart Contract Address and ABI Path
auth_contract_address = "0x023232ca2255642eF3A181D92384aE0e6fbfadfF"
auth_abi_file_path = r"C:\Users\WINDOWS\Documents\CSS453_SEiMCS\build\contracts\AuthContract.json"

# Load ABI
try:
    with open(auth_abi_file_path, "r") as abi_file:
        auth_contract_abi = json.load(abi_file)["abi"]
except FileNotFoundError:
    raise Exception(f"ABI file not found at {auth_abi_file_path}")

auth_contract = web3.eth.contract(address=auth_contract_address, abi=auth_contract_abi)

# Hash Password
def hash_password(password):
    return Web3.solidity_keccak(['string'], [password])

# Register User
try:
    user_address = web3.to_checksum_address("0x1D54DaC973DC3fAB89c5e344C5685Ce296b134D4")
    password_hash = hash_password("password123")

    print(f"Registering user: {user_address}")
    print(f"Generated Password Hash: {password_hash}")

    # Build the transaction (without role)
    txn = auth_contract.functions.registerUser(user_address, password_hash).build_transaction({
        'from': web3.eth.accounts[0],
        'gas': 3000000,
        'nonce': web3.eth.get_transaction_count(web3.eth.accounts[0]),
    })

    # Sign and send the transaction
    private_key = "0xeda64e1dae3e76d1060075d1a31a919f66dea29f2cf3af1bab60da49f61d248a"
    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

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

