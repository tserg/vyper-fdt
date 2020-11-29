var FundsDistributionToken = artifacts.require("FundsDistributionToken")

module.exports = function(deployer) {
	deployer.deploy(FundsDistributionToken, "MetaCoin", "MCC", 0, 100);
};