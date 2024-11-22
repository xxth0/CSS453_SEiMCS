from web3 import Web3

# Ganache RPC URL
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Check connection
if not web3.is_connected():
    print("Failed to connect to Ganache")
    exit()

# Contract details
contract_address = "0x9475074e0996Cc1Cbbe42d0Bd4d2d95bB87bF631"
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
    }
]

# Load the contract
contract = web3.eth.contract(address=contract_address, abi=abi)

# Private key and account
private_key = "0x18ad8276275d39273eed2047ff0aa688020a241cfdb4c51c82a1b7d4d7044daf"
account = web3.eth.account.from_key(private_key)

# Function to store CID on the blockchain
def store_file_on_blockchain(cid, file_path):
    transaction = contract.functions.storeFile(cid, file_path).build_transaction({
        "from": account.address,
        "nonce": web3.eth.get_transaction_count(account.address),
        "gas": 2000000,
        "gasPrice": web3.to_wei("20", "gwei"),
    })

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    return web3.to_hex(tx_hash)

# Read CIDs from indexes.txt and store them on blockchain
indexes_file = "indexes.txt"
with open(indexes_file, "r") as file:
    for line in file:
        parts = line.strip().split(" ")
        cid = parts[1]
        file_path = " ".join(parts[2:])  # Join file path if it contains spaces
        tx_hash = store_file_on_blockchain(cid, file_path)
        print(f"Stored CID {cid} with TxHash: {tx_hash}")
