from web3 import Web3
import json

# Connect to Ganache
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

if not web3.is_connected():
    raise Exception("Failed to connect to Ganache")
print("Connected to Blockchain")

# Smart Contract Address and ABI Path
contract_address = "0x1fC48E6d7F8e8fC7BCB85176580811A334204239"
abi_path = "C:/Users/WINDOWS/Documents/CSS453_SEiMCS/build/contracts/AuthContract.json"

# Load Contract ABI
try:
    with open(abi_path, "r") as f:
        contract_abi = json.load(f)["abi"]
except FileNotFoundError:
    raise Exception(f"ABI file not found at {abi_path}")

auth_contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Function to hash password
def hash_password(password):
    return Web3.solidity_keccak(['string'], [password])

# Test Authentication
try:
    # Define the user address and password
    user_address = web3.to_checksum_address("0x7da0dC9C63d3927cB251D6BA1519b1A0cD8CE549")
    test_password = "password123"

    # Fetch the stored password hash
    stored_hash = auth_contract.functions.getStoredHash(user_address).call()
    print(f"Stored Password Hash: {stored_hash}")

    # Generate the password hash for testing
    password_hash = hash_password(test_password)
    print(f"Generated Password Hash: {password_hash}")

    # Compare hashes
    if stored_hash == password_hash:
        print("Hashes match! Proceeding to test authentication...")

        # Call the authenticate function
        authenticated = auth_contract.functions.authenticate(user_address, password_hash).call()
        if authenticated:
            print("Authentication successful!")
        else:
            print("Authentication failed: Password hash matches, but smart contract rejected the login.")
    else:
        print("Hashes do NOT match! Ensure the correct password was provided and the user is registered.")

except Exception as e:
    print(f"Error during authentication test: {e}")
