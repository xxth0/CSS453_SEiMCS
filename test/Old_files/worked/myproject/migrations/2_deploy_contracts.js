const AuthContract = artifacts.require("AuthContract");

module.exports = function (deployer) {
  deployer.deploy(AuthContract);
};
