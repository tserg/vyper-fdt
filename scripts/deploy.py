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

	'''
	tx = fdt_factory.deploy_fdt_contract(
		'Musicakes',
		'MCAKES',
		0,
		100
	)

	fdt_instance = FundsDistributionToken.at(tx.new_contracts[0])
	print("Address of Musicakes instance: " + str(fdt_instance))
	'''
