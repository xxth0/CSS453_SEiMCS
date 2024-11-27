// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AuthContract {
    // Store user credentials (hashed password) and roles
    mapping(address => string) private userPasswordHashes;
    mapping(address => string) private userRoles;

    // Event to log successful authentication
    event AuthenticationSuccess(address user, string role);

    // Function to register a user with their password hash and role
    function registerUser(address userAddress, string memory passwordHash, string memory role) public {
        userPasswordHashes[userAddress] = passwordHash;
        userRoles[userAddress] = role;
    }

    // Function to authenticate a user by comparing password hash
    function authenticate(address userAddress, string memory passwordHash) public returns (bool) {
        // Check if the provided password hash matches the stored hash
        if (keccak256(abi.encodePacked(passwordHash)) == keccak256(abi.encodePacked(userPasswordHashes[userAddress]))) {
            string memory role = userRoles[userAddress];
            emit AuthenticationSuccess(userAddress, role);
            return true;  // Authentication success
        } else {
            return false;  // Authentication failed
        }
    }

    // Function to get the role of a user
    function getRole(address userAddress) public view returns (string memory) {
        return userRoles[userAddress];
    }
}
