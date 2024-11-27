from flask import Flask, request, render_template, flash, session, send_file, jsonify, request, url_for, send_from_directory, redirect
from fuzzywuzzy import fuzz
from werkzeug.utils import secure_filename
import requests
import os
import hashlib
from web3 import Web3
import json
import threading
from time import time

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64


app = Flask(__name__)

IPFS_GATEWAY = "http://127.0.0.1:8080/ipfs/"

# Connect to Ganache
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

if not web3.is_connected():
    raise Exception("Failed to connect to Ganache")
print("Connected to Blockchain")

# Smart Contract Details
search_abi_file_path = r"C:\Users\WINDOWS\Documents\CSS453_SEiMCS\build\contracts\StoreCIDs.json"
with open(search_abi_file_path, "r") as abi_file:
    search_contract_abi = json.load(abi_file)["abi"]
search_contract_address = "0xA6c087338F11b08DD39c2765e89BEA083057167F"  # Replace with your contract address
search_contract = web3.eth.contract(address=search_contract_address, abi=search_contract_abi)

# Load ABI
auth_abi_file_path = r"C:/Users/WINDOWS/Documents/CSS453_SEiMCS/build/contracts/AuthContract.json"
with open(auth_abi_file_path, "r") as abi_file:
    auth_contract_abi = json.load(abi_file)["abi"]
auth_contract_address = "0x023232ca2255642eF3A181D92384aE0e6fbfadfF"
auth_contract = web3.eth.contract(address=auth_contract_address, abi=auth_contract_abi)

# Path to auxiliary indexes
auxiliary_path = "C:/Users/WINDOWS/Documents/CSS453_SEiMCS/Auxiliary_Tree_Hashed"

# Define directories for temporary file storage
UPLOAD_FOLDER = 'uploads'
DECRYPTED_FOLDER = 'decrypted'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DECRYPTED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DECRYPTED_FOLDER'] = DECRYPTED_FOLDER

def generate_rsa_key_pair():
    key = RSA.generate(2048)
    return key.publickey(), key

def generate_trapdoor(user_credentials, pub_key):
    cipher_rsa = PKCS1_OAEP.new(pub_key)
    return cipher_rsa.encrypt(user_credentials.encode('utf-8'))

# Function to hash passwords using Keccak (same as Solidity)
def hash_password(password):
    return Web3.solidity_keccak(['string'], [password])

# Function to authenticate user by interacting with the smart contract
def authenticate_user(user_address, password):
    try:
        # Hash the password
        password_hash = hash_password(password)
        app.logger.debug(f"Generated Password Hash: {password_hash}")

        # Retrieve stored hash from the smart contract
        stored_hash = auth_contract.functions.getStoredHash(user_address).call()
        app.logger.debug(f"Stored Password Hash: {stored_hash}")

        # Check if hashes match
        if stored_hash == password_hash:
            app.logger.debug("Hashes match! Proceeding to smart contract authentication...")

            # Call the authenticate function in the smart contract
            authenticated = auth_contract.functions.authenticate(user_address, password_hash).call()
            app.logger.debug(f"Authentication Result from Smart Contract: {authenticated}")
            return authenticated
        else:
            app.logger.error("Hashes do NOT match!")
            return False
    except Exception as e:
        app.logger.error(f"Error during authentication: {e}")
        return False

# AES utility functions
def get_aes_key(user_key):
    return hashlib.md5(user_key.encode('utf-8')).digest()

def unpad_data(data):
    padding_len = data[-1]
    return data[:-padding_len]

def decrypt_file(input_file_path, output_file_path, key):
    # Create the AES cipher in ECB mode
    cipher = AES.new(key, AES.MODE_ECB)

    # Read the encrypted file data
    with open(input_file_path, 'rb') as f:
        encrypted_data = f.read()

    # Decrypt and unpad the data
    decrypted_data = unpad_data(cipher.decrypt(encrypted_data))

    # Write the decrypted data to a new file
    with open(output_file_path, 'wb') as df:
        df.write(decrypted_data)

def decrypt_data(encrypted_data):
    """Decrypt AES-encrypted data."""
    try:
        processed_key = base64.b64decode("dmwxbTBSV0ZISXRUV3VrTQ==")
        cipher = AES.new(processed_key, AES.MODE_ECB)
        decoded = base64.b64decode(encrypted_data)
        return unpad(cipher.decrypt(decoded), AES.block_size).decode('utf-8')
    except Exception as e:
        raise Exception(f"Decryption failed: {str(e)}")


app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default-key-for-local-dev")

# Function to hash PID
def hash_pid(pid):
    return hashlib.sha256(pid.encode()).hexdigest()

# Function to retrieve CID for a hashed PID
def get_cid(hashed_pid):
    try:
        return search_contract.functions.getCID(hashed_pid).call()
    except Exception as e:
        print(f"Error querying CID for hashed PID: {hashed_pid} -> {e}")
        return None

 # One of the operation requirement (Search in Range)
def search_pids_in_range(start, end):
    range_pids = []
    for i in range(int(start), int(end) + 1):
        for _ in range(3):  # Redundant traversal 3 times
            range_pids.append(str(i))
    return range_pids


def hash_keyword(keyword):
    return hashlib.sha256(keyword.encode()).hexdigest()

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]  # Swap
    return arr


def search_auxiliary(keywords):
    results = None  # Initialize as None to compute intersection

    for filename in os.listdir(auxiliary_path):
        if filename.endswith(".txt"):
            with open(os.path.join(auxiliary_path, filename), 'r') as file:
                lines = file.readlines()

                # Process each keyword multiple times to add redundancy
                for keyword in keywords:
                    for _ in range(3):  # Repeat the process for each keyword three times
                        hashed_keyword = hash_keyword(keyword)  # Hash the input keyword

                        # Iterate through the lines to find matching keywords
                        for i, line in enumerate(lines):
                            if hashed_keyword in line:  # Match hashed keyword
                                # The next line contains the PIDs
                                if i + 1 < len(lines):
                                    pids = set(lines[i + 1].strip().split(", "))

                                    # Redundant sorting of PIDs before storing
                                    sorted_pids = sorted(pids)  # First sort
                                    sorted_pids = bubble_sort(list(pids))  # Convert set to list if necessary  # Sort again

                                    # Update the results with intersection
                                    if results is None:
                                        results = set(sorted_pids)  # Initialize the intersection set
                                    else:
                                        results &= set(sorted_pids)  # Intersect with existing results
                                break  # Stop searching after finding the keyword
    return results or set()  # Return an empty set if no matches are found



# Log incoming JSON requests
@app.before_request
def log_request_info():
    if request.is_json:
        app.logger.debug(f"Incoming JSON: {request.json}")
    else:
        app.logger.debug(f"Incoming Form Data: {request.form}")


# Login route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            # Parse input data
            if request.is_json:
                data = request.json
                username = data.get("username")
                password = data.get("password")
            else:
                username = request.form.get("username")
                password = request.form.get("password")

            app.logger.debug(f"Login attempt - Username: {username}, Password: [HIDDEN]")

            # Validate input
            if not username or not password:
                return jsonify({"success": False, "message": "Username and password are required"}), 400

            # Validate Ethereum address format
            try:
                user_address = web3.to_checksum_address(username)
            except ValueError:
                return jsonify({"success": False, "message": "Invalid Ethereum address format"}), 400

            # Authenticate user
            is_authenticated = authenticate_user(user_address, password)
            if is_authenticated:
                # Set session variable on successful login
                session["username"] = user_address
                app.logger.debug(f"Session set for user: {session['username']}")
                return jsonify({"success": True, "message": "Authentication successful", "redirect": "/main"}), 200
            else:
                return jsonify({"success": False, "message": "Invalid credentials. Please try again."}), 401

        except Exception as e:
            app.logger.error(f"Exception during login: {e}")
            return jsonify({"success": False, "message": "An error occurred. Please try again."}), 500

    # Render the login page for GET requests
    return render_template("index.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/main")
def main():
    if "username" not in session:
        return redirect("/")
    return render_template("main.html", username=session["username"])

@app.route('/download', methods=['GET'])
def download_file():
    if "username" not in session:
        return redirect("/")
    cid = request.args.get('cid')
    if not cid:
        app.logger.error("CID is required but not provided.")
        return jsonify({"error": "CID is required"}), 400

    # Define the IPFS gateway URL
    ipfs_url = f"http://127.0.0.1:8080/ipfs/{cid}"
    tmp_dir = os.path.join(os.getcwd(), 'uploads/tmp')  # Custom temp directory
    os.makedirs(tmp_dir, exist_ok=True)  # Ensure the directory exists
    tmp_file_path = os.path.join(tmp_dir, f"{cid}.dat")  # Save as .dat

    try:
        # Fetch the file from IPFS
        app.logger.debug(f"Fetching file from IPFS: {ipfs_url}")
        response = requests.get(ipfs_url, stream=True)

        if response.status_code != 200:
            app.logger.error(f"IPFS response error: {response.status_code}, {response.text}")
            return jsonify({"error": f"Failed to fetch file from IPFS. Status code: {response.status_code}"}), 500

        # Save the file temporarily
        app.logger.debug(f"Saving file temporarily to: {tmp_file_path}")
        with open(tmp_file_path, 'wb') as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    tmp_file.write(chunk)

        # Stream the file to the client
        app.logger.debug(f"Serving file with .dat extension from: {tmp_file_path}")
        return send_file(
            tmp_file_path,
            as_attachment=True,
            download_name=f"{cid}.dat",
            mimetype="application/octet-stream"
        )

    except Exception as e:
        app.logger.error(f"Error during file download: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    finally:
        # Schedule file deletion using a background thread
        def cleanup_file(file_path):
            try:
                if os.path.exists(file_path):
                    time.sleep(1)  # Ensure the file is not in use
                    os.remove(file_path)
                    app.logger.debug(f"Removed temporary file: {file_path}")
            except Exception as e:
                app.logger.error(f"Failed to remove temporary file: {file_path}. Error: {str(e)}")

        threading.Thread(target=cleanup_file, args=(tmp_file_path,)).start()


@app.route('/search', methods=['POST'])
def search():
    if "username" not in session:
        return redirect("/")
    try:
        # Log the received encrypted query
        encrypted_query = request.form['query']
        app.logger.debug(f"Received Encrypted Query: {encrypted_query}")

        # Attempt to decrypt the query
        decrypted_query = decrypt_data(encrypted_query)
        app.logger.debug(f"Decrypted Query: {decrypted_query}")

        # Split the decrypted query into individual inputs
        inputs = decrypted_query.split(",")
        inputs = [item.strip() for item in inputs]

        # Validate decrypted inputs
        if not decrypted_query.strip():
            flash("Search query cannot be empty. Please provide a valid keyword or PID.", "error")
            return render_template('main.html')

        if all(not item.isnumeric() and len(item) < 3 for item in inputs):
            flash("Please enter valid keywords (at least 3 characters) or numeric PIDs.", "error")
            return render_template('main.html')

        start_time = time()

        # Initialize results storage
        keyword_results = {"cids": {}}
        pid_results = {}
        intersection_pids = set()

        # Process inputs
        search_start_time = time()
        for input_item in inputs:
            # Range Search
            if '-' in input_item and all(part.isdigit() for part in input_item.split('-')):
                start, end = map(int, input_item.split('-'))
                range_pids = set(search_pids_in_range(start, end))
                if not intersection_pids:
                    intersection_pids = range_pids
                else:
                    intersection_pids &= range_pids
                continue

            # NOT Operation
            elif input_item.startswith('NOT:'):
                not_keyword = input_item.replace('NOT:', '').strip()
                excluded_pids = set(search_auxiliary([not_keyword]))
                if intersection_pids:
                    intersection_pids -= excluded_pids
                continue

            # OR Operation
            elif input_item.startswith('OR:'):
                or_keywords = input_item.replace('OR:', '').split('|')
                or_results = set()
                for keyword in or_keywords:
                    keyword = keyword.strip()

                    # Handle ranges within OR operation
                    if '-' in keyword and all(part.isdigit() for part in keyword.split('-')):
                        start, end = map(int, keyword.split('-'))
                        or_results |= set(search_pids_in_range(start, end))
                    else:
                        # Default to keyword search
                        or_results |= set(search_auxiliary([keyword]))
    
                if not intersection_pids:
                    intersection_pids = or_results
                else:
                    intersection_pids |= or_results
                continue

            # PID Search
            elif input_item.isnumeric():
                hashed_pid = hash_pid(input_item)
                cid = get_cid(hashed_pid)
                pid_results[input_item] = {"hashed_pid": hashed_pid, "cid": cid}
                continue

            # Default: Keyword Search
            else:
                matching_pids = set(search_auxiliary([input_item]))
                if not intersection_pids:
                    intersection_pids = matching_pids
                else:
                    intersection_pids &= matching_pids
        search_end_time = time()

        # Sort and hash PIDs from the keyword intersection
        sort_start_time = time()
        if intersection_pids:
            sorted_pids = sorted(intersection_pids, key=int)  # Sort numerically
            hashed_pids = [hash_pid(pid) for pid in sorted_pids]
            keyword_results["cids"] = {
                pid: get_cid(hpid) for pid, hpid in zip(sorted_pids, hashed_pids)
            }
        sort_end_time = time()

        end_time = time()

        app.logger.debug(f"PID Results: {pid_results}")
        app.logger.debug(f"Keyword Results: {keyword_results}")

        # Render the results page
        return render_template(
            'results.html',
            keywords=decrypted_query,  # Show the decrypted query in results
            pid_results=pid_results,
            keyword_results=keyword_results,
            search_time=round(end_time - start_time, 4),
            search_phase_time=round(search_end_time - search_start_time, 4),
            sort_phase_time=round(sort_end_time - sort_start_time, 4),
            hash_pid=hash_pid
        )
    except Exception as e:
        app.logger.error(f"Decryption or Processing failed: {str(e)}")
        flash("An error occurred during the search process. Please try again.", "error")
        return render_template('main.html')


@app.route('/dec', methods=['GET', 'POST'])
def decrypt():
    if "username" not in session:
        return redirect("/")
    if request.method == 'POST':
        try:
            # Get user inputs
            key = request.form.get('key')
            file = request.files.get('file')

            # Validate inputs
            if not key or not file:
                flash("Both the key and file are required for decryption.", "error")
                return redirect('/dec')

            # Secure the file name and save it temporarily
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)

            # Generate the AES key
            aes_key = get_aes_key(key)

            # Define the output file name with a .csv extension
            base_name = os.path.splitext(filename)[0]  # Remove existing extension
            output_filename = f"{base_name}_decrypted.csv"
            output_path = os.path.join(app.config['DECRYPTED_FOLDER'], output_filename)

            # Perform decryption
            app.logger.debug(f"Decrypting file: {input_path} to {output_path}")
            decrypt_file(input_path, output_path, aes_key)

            # Provide the download link
            app.logger.debug(f"Decryption successful. File saved to: {output_path}")
            return render_template(
                'dec.html',
                decrypted_file=url_for('download_decrypted_file', filename=output_filename)
            )

        except Exception as e:
            app.logger.error(f"Decryption failed: {str(e)}")
            flash(f"Decryption failed: {str(e)}", "error")
            return redirect('/dec')

    # Render the decryption page for GET requests
    return render_template('dec.html')



@app.route('/decrypted/<filename>')
def download_decrypted_file(filename):
    if "username" not in session:
        return redirect("/")
    return send_from_directory(app.config['DECRYPTED_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)
