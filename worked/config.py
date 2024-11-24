ganache_url = "http://127.0.0.1:7545"
contract_address = "0xa81cDf37d00Be5d27644F26Ef6540eB46188896A"  # Replace with your contract address
contract_abi = [
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "address",
          "name": "user",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "role",
          "type": "string"
        }
      ],
      "name": "AuthenticationSuccess",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "userAddress",
          "type": "address"
        },
        {
          "internalType": "string",
          "name": "passwordHash",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "role",
          "type": "string"
        }
      ],
      "name": "registerUser",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "userAddress",
          "type": "address"
        },
        {
          "internalType": "string",
          "name": "passwordHash",
          "type": "string"
        }
      ],
      "name": "authenticate",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "userAddress",
          "type": "address"
        }
      ],
      "name": "getRole",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    }
  ]
