const FileIndex  = artifacts.require("FileIndex");

module.exports = function (deployer) {
    deployer.deploy(FileIndex);
};
