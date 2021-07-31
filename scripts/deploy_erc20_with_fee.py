from brownie import (
	ERC20,
	FeeGovernor,
	FeeGovernorProxy,
	FundsDistributionTokenERC20WithFee,
	FundsDistributionTokenERC20WithFeeFactory,
	accounts,
)

def main():
	acct = accounts.load('deployment_account')

	erc20 = ERC20.deploy("Base Token", "BASE", 18, 200e18, {'from': acct})
	#print(erc20.address)
	fg = FeeGovernor.deploy(1e8, {'from': acct})
	fgp = FeeGovernorProxy.deploy(fg.address, {'from': acct})

	fdt_erc20_wf = FundsDistributionTokenERC20WithFee.deploy({'from': acct})
	fdt_erc20_wf_factory = FundsDistributionTokenERC20WithFeeFactory.deploy(
		fdt_erc20_wf, acct, erc20.address, fgp.address, {'from': acct}
	)
	# FundsDistributionToken.deploy('Musicakes', 'MCAKES', 0, 100, {'from': acct})

	'''
	tx = fdt_erc20_wf_factory.deploy_fdt_contract(
		'Musicakes',
		'MCAKES',
		0,
		100
	)

	fdt_instance = FundsDistributionTokenERC20WithFee.at(tx.new_contracts[0])
	print("Address of Musicakes instance: " + str(fdt_instance))
	'''
