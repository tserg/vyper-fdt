from brownie import (
	ERC20,
	FundsDistributionTokenERC20,
	FundsDistributionTokenERC20Factory,
	accounts,
)

def main():
	acct = accounts[0]

	erc20 = ERC20.deploy("Base Token", "BASE", 18, 200e18, {'from': acct})
	print(erc20.address)

	fdt_erc20 = FundsDistributionTokenERC20.deploy({'from': acct})
	fdt_erc20_factory = FundsDistributionTokenERC20Factory.deploy(
		fdt_erc20, acct, {'from': acct}
	)
	# FundsDistributionToken.deploy('Musicakes', 'MCAKES', 0, 100, {'from': acct})

	tx = fdt_erc20_factory.deploy_fdt_contract(
		'Musicakes',
		'MCAKES',
		0,
		100,
		erc20.address
	)

	fdt_instance = FundsDistributionTokenERC20.at(tx.new_contracts[0])
	print("Address of Musicakes instance: " + str(fdt_instance))
