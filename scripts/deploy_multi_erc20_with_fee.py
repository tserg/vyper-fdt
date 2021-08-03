from brownie import (
	ERC20,
	FeeGovernor,
	FeeGovernorProxy,
	PaymentTokenGovernor,
	PaymentTokenGovernorProxy,
	FundsDistributionTokenMultiERC20WithFee,
	FundsDistributionTokenMultiERC20WithFeeFactory,
	accounts,
)

def main():
	#acct = accounts.load('deployment_account')
	acct = accounts[0]

	# Deploy payment token

	erc20 = ERC20.deploy("Base Token", "BASE", 18, 200e18, {'from': acct})

	# Deploy PaymentTokenGovernor and PaymentTokenGovernorProxy,
	# then add payment token to PaymentTokenGovernor

	payment_token_governor = PaymentTokenGovernor.deploy({'from': acct})
	payment_token_governor_proxy = PaymentTokenGovernorProxy.deploy(
		payment_token_governor.address,
		{'from': acct}
	)
	add_payment_token_to_governor = PaymentTokenGovernor[0].add_payment_token(
		erc20.address,
		{'from': acct}
	)

	# Deploy FeeGovernor with 1% fee and FeeGovernorProxy

	fee_governor = FeeGovernor.deploy(1e8, {'from': acct})
	fee_governor_proxy = FeeGovernorProxy.deploy(fee_governor.address, {'from': acct})

	fdt_multi_erc20_wf = FundsDistributionTokenMultiERC20WithFee.deploy({'from': acct})
	fdt_multi_erc20_wf_factory = FundsDistributionTokenMultiERC20WithFeeFactory.deploy(
		fdt_multi_erc20_wf,
		acct,
		payment_token_governor_proxy.address,
		fee_governor_proxy.address,
		{'from': acct}
	)
	# FundsDistributionToken.deploy('Musicakes', 'MCAKES', 0, 100, {'from': acct})

	tx = fdt_multi_erc20_wf_factory.deploy_fdt_contract(
		'Musicakes',
		'MCAKES',
		0,
		100
	)

	fdt_instance = FundsDistributionTokenMultiERC20WithFee.at(tx.new_contracts[0])
	print("Address of Musicakes instance: " + str(fdt_instance))
