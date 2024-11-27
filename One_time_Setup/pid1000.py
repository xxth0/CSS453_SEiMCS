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
contract_address = "0xA6c087338F11b08DD39c2765e89BEA083057167F"
abi_file_path = r"C:\Users\WINDOWS\Documents\CSS453_SEiMCS\build\contracts\StoreCIDs.json"

# Load ABI from the specified path
with open(abi_file_path, "r") as abi_file:
    contract_abi = json.load(abi_file)["abi"]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Private key and account derived from it
private_key = "0xeda64e1dae3e76d1060075d1a31a919f66dea29f2cf3af1bab60da49f61d248a"
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
            "chainId": 1337,  # Ganache's default chain ID
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

# Upload PID 1000
pid = "1000"
cid = "QmTP86FfrtE1atwdEw7bH5k68piNVox4NtpsxdxzKkCh7p"
hpid = hash_pid(pid)

print(f"Uploading PID: {pid}, HPID: {hpid}, CID: {cid}")
send_transaction(hpid, cid)
