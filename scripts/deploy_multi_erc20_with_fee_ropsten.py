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

DAI_ADDRESS = '0xad6d458402f60fd3bd25163575031acdce07538d'
USDC_ADDRESS = '0x07865c6e87b9f70255377e024ace6630c1eaa37f'

def main():
	acct = accounts.load('deployment_account')

	# Deploy PaymentTokenGovernor and PaymentTokenGovernorProxy,
	# then add payment token to PaymentTokenGovernor

	payment_token_governor = PaymentTokenGovernor.deploy({'from': acct})
	payment_token_governor_proxy = PaymentTokenGovernorProxy.deploy(
		payment_token_governor.address,
		{'from': acct}
	)
	add_payment_token_to_governor = payment_token_governor.add_payment_token(
		DAI_ADDRESS,
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
