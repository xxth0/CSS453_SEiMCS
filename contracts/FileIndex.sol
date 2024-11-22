// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FileIndex {
    struct File {
        string cid;
        string filePath;
        address uploader;
    }

    mapping(uint256 => File) public files;
    uint256 public fileCount;

    event FileStored(uint256 indexed fileId, string cid, string filePath, address indexed uploader);

    function storeFile(string memory _cid, string memory _filePath) public {
        files[fileCount] = File(_cid, _filePath, msg.sender);
        emit FileStored(fileCount, _cid, _filePath, msg.sender);
        fileCount++;
    }

    function getFile(uint256 _fileId) public view returns (string memory, string memory, address) {
        File memory file = files[_fileId];
        return (file.cid, file.filePath, file.uploader);
    }
}
