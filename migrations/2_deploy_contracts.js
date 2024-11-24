const AuthContract = artifacts.require("AuthContract");
const StoreCIDs = artifacts.require("StoreCIDs");

module.exports = function (deployer) {
    // Deploy AuthContract
    deployer.deploy(AuthContract);

    // Deploy StoreCIDs
    deployer.deploy(StoreCIDs);
};
