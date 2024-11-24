from web3 import Web3
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from config import ganache_url, contract_address, contract_abi

# Connect to Ganache
web3 = Web3(Web3.HTTPProvider(ganache_url))

if not web3.is_connected():
    print("Failed to connect to Ganache.")
    exit()

# Create contract instance
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Step 1: RSA Key Pair Generation and Trapdoor Creation
def generate_rsa_key_pair():
    key = RSA.generate(2048)  # Generate RSA key pair
    return key.publickey(), key

def generate_trapdoor(user_credentials, pub_key):
    cipher_rsa = PKCS1_OAEP.new(pub_key)
    trapdoor = cipher_rsa.encrypt(user_credentials.encode('utf-8'))  # Encrypt credentials only
    return trapdoor


# Step 2: Authenticate User by Calling the Smart Contract
def authenticate_user(user_address, password):
    # Hash the password
    password_hash = hashlib.md5(password.encode()).hexdigest()

    # Call the smart contract's authenticate function
    authenticated = contract.functions.authenticate(user_address, password_hash).call()
    
    if authenticated:
        role = contract.functions.getRole(user_address).call()
        print(f"User authenticated. Role: {role}")
        return True, role
    else:
        print("Authentication failed.")
        return False, None

# Step 3: Register User in the Smart Contract (for testing)
def register_user(user_address, password, role):
    password_hash = hashlib.md5(password.encode()).hexdigest()  # Hash the password
    contract.functions.registerUser(user_address, password_hash, role).transact({'from': web3.eth.accounts[0]})  # Register user in the smart contract
    print(f"User {role} registered.")

# Main Program to Run Authentication Process
def main():
    username = "john_doe"
    password = "password123"
    
    # Generate RSA key pair for encryption
    pub_key, priv_key = generate_rsa_key_pair()

    # Generate the trapdoor (encrypt credentials only, no search query yet)
    user_credentials = username + "|" + password
    trapdoor = generate_trapdoor(user_credentials, pub_key)

    # Test: Register John Doe as Doctor (for the first time)
    john_doe_address = "0x16B8920F8478BC60d39e880bF8263d1125bC0Cc5"  # Replace with John Doe's Ethereum address
    register_user(john_doe_address, password, "Doctor")

    # Authenticate John Doe via smart contract
    is_valid, role = authenticate_user(john_doe_address, password)
    if is_valid:
        print(f"User authenticated. Role: {role}. Proceeding with search if needed.")
    else:
        print("Authentication failed.")


if __name__ == "__main__":
    main()
