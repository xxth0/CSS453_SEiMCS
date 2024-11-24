const StoreCIDs = artifacts.require("StoreCIDs");

module.exports = function (deployer) {
    deployer.deploy(StoreCIDs);
};
