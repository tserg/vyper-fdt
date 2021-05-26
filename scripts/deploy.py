from brownie import (
	FundsDistributionToken,
	FundsDistributionTokenFactory,
	accounts,
)

def main():
	acct = accounts.load('deployment_account')
	fdt = FundsDistributionToken.deploy({'from': acct})
	fdt_factory = FundsDistributionTokenFactory.deploy(
		fdt, acct, {'from': acct}
	)
	# FundsDistributionToken.deploy('Musicakes', 'MCAKES', 0, 100, {'from': acct})
