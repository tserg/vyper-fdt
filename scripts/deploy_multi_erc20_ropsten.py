from brownie import (
	ERC20,
	PaymentTokenGovernor,
	PaymentTokenGovernorProxy,
	FundsDistributionTokenMultiERC20,
	FundsDistributionTokenMultiERC20Factory,
	accounts,
)

DAI_ADDRESS = '0xad6d458402f60fd3bd25163575031acdce07538d'

def main():
	acct = accounts.load('deployment_account')

	paymentTokenGovernor = PaymentTokenGovernor.deploy({'from': acct})

	paymentTokenGovernorProxy = PaymentTokenGovernorProxy.deploy(paymentTokenGovernor.address, {'from': acct})

	add_payment_token_to_governor = PaymentTokenGovernor[0].add_payment_token(DAI_ADDRESS, {'from': acct})

	fdt_multi_erc20 = FundsDistributionTokenMultiERC20.deploy({'from': acct})
	fdt_multi_erc20_factory = FundsDistributionTokenMultiERC20Factory.deploy(
		fdt_multi_erc20, acct, paymentTokenGovernorProxy.address, {'from': acct}
	)

	tx = fdt_multi_erc20_factory.deploy_fdt_contract(
		'Musicakes',
		'MCAKES',
		0,
		100
	)

	fdt_instance = FundsDistributionTokenMultiERC20.at(tx.new_contracts[0])
	print("Address of Musicakes instance: " + str(fdt_instance))
