// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract StoreCIDs {
    // Mapping from hashed PID to CID
    mapping(string => string) private hashedPidToCid;

    // Event to log when a new mapping is added
    event MappingAdded(string hashedPid, string cid);

    // Function to add a hashed PID -> CID mapping
    function addMapping(string memory hashedPid, string memory cid) public {
        require(bytes(hashedPid).length > 0, "Hashed PID cannot be empty");
        require(bytes(cid).length > 0, "CID cannot be empty");
        require(bytes(hashedPidToCid[hashedPid]).length == 0, "Hashed PID already exists");

        hashedPidToCid[hashedPid] = cid;

        emit MappingAdded(hashedPid, cid);
    }

    // Function to retrieve a CID using a hashed PID
    function getCID(string memory hashedPid) public view returns (string memory) {
        require(bytes(hashedPid).length > 0, "Hashed PID cannot be empty");
        string memory cid = hashedPidToCid[hashedPid];
        require(bytes(cid).length > 0, "CID not found for the provided hashed PID");
        return cid;
    }
}
