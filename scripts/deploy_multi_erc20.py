from brownie import (
	ERC20,
	PaymentTokenGovernor,
	PaymentTokenGovernorProxy,
	FundsDistributionTokenMultiERC20,
	FundsDistributionTokenMultiERC20Factory,
	accounts,
)

def main():
	#acct = accounts.load('deployment_account')
	acct = accounts[0]

	paymentTokenGovernor = PaymentTokenGovernor.deploy({'from': acct})

	paymentTokenGovernorProxy = PaymentTokenGovernorProxy.deploy(paymentTokenGovernor.address, {'from': acct})

	erc20 = ERC20.deploy("Base Token", "BASE", 18, 200e18, {'from': acct})
	#print(erc20.address)

	add_payment_token_to_governor = PaymentTokenGovernor[0].add_payment_token(erc20.address, {'from': acct})

	fdt_multi_erc20 = FundsDistributionTokenMultiERC20.deploy({'from': acct})
	fdt_multi_erc20_factory = FundsDistributionTokenMultiERC20Factory.deploy(
		fdt_multi_erc20, acct, paymentTokenGovernorProxy.address, {'from': acct}
	)
	# FundsDistributionToken.deploy('Musicakes', 'MCAKES', 0, 100, {'from': acct})


	tx = fdt_multi_erc20_factory.deploy_fdt_contract(
		'Musicakes',
		'MCAKES',
		0,
		100
	)

	fdt_instance = FundsDistributionTokenMultiERC20.at(tx.new_contracts[0])
	print("Address of Musicakes instance: " + str(fdt_instance))
