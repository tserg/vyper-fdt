var FundsDistributionToken = artifacts.require("FundsDistributionToken")

module.exports = function(deployer) {
	deployer.deploy(FundsDistributionToken, "MetaCoin", "MCC", 18, 100000);
};