// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AuthContract {
    // Store user credentials (hashed password)
    mapping(address => bytes32) private userPasswordHashes;

    // Register a new user with a hashed password
    function registerUser(address userAddress, bytes32 passwordHash) public {
        require(userAddress != address(0), "Invalid address");
        require(userPasswordHashes[userAddress] == 0, "User already registered");

        // Store the hashed password
        userPasswordHashes[userAddress] = passwordHash;

        // Check if the hash was stored correctly
        require(userPasswordHashes[userAddress] == passwordHash, "Hash not stored correctly");
    }

    // Authenticate a user with a hashed password
    function authenticate(address userAddress, bytes32 passwordHash) public view returns (bool) {
        return userPasswordHashes[userAddress] == passwordHash;
    }

    // Retrieve the hashed password for debugging (optional, should be restricted in production)
    function getStoredHash(address userAddress) public view returns (bytes32) {
        return userPasswordHashes[userAddress];
    }
}
