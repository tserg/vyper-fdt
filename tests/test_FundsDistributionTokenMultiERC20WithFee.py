import pytest

from brownie import (
	accounts,
	chain,
	reverts,
	ERC20,
	PaymentTokenGovernor,
	PaymentTokenGovernorProxy,
	FundsDistributionTokenMultiERC20WithFee,
	FundsDistributionTokenMultiERC20WithFeeFactory,
)

PAYMENT_TOKEN_NAME = "Sai"
PAYMENT_TOKEN_SYMBOL = "SAI"
PAYMENT_TOKEN_DECIMALS = 18
PAYMENT_TOKEN_SUPPLY = 1000e18

NEW_PAYMENT_TOKEN_NAME = "Dai"
NEW_PAYMENT_TOKEN_SYMBOL = "DAI"
NEW_PAYMENT_TOKEN_DECIMALS = 18
NEW_PAYMENT_TOKEN_SUPPLY = 1000e18

TOKEN_NAME = "MetaCoin"
TOKEN_SYMBOL = "MCC"
TOKEN_DECIMALS = 0
TOKEN_SUPPLY = 100

ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

@pytest.fixture(scope="module")
def PaymentToken(ERC20, accounts):
	yield ERC20.deploy(PAYMENT_TOKEN_NAME, PAYMENT_TOKEN_SYMBOL, PAYMENT_TOKEN_DECIMALS, PAYMENT_TOKEN_SUPPLY, {'from': accounts[0]})

@pytest.fixture(scope="module")
def NewPaymentToken(ERC20, accounts):
	yield ERC20.deploy(NEW_PAYMENT_TOKEN_NAME, NEW_PAYMENT_TOKEN_SYMBOL, NEW_PAYMENT_TOKEN_DECIMALS, NEW_PAYMENT_TOKEN_SUPPLY, {'from': accounts[0]})

@pytest.fixture(scope="module", autouse=True)
def PaymentTokenGovernorContract(PaymentTokenGovernor, accounts):
	yield PaymentTokenGovernor.deploy({'from': accounts[0]})

@pytest.fixture(scope="module", autouse=True)
def NewPaymentTokenGovernorContract(PaymentTokenGovernor, accounts):
	yield PaymentTokenGovernor.deploy({'from': accounts[0]})

@pytest.fixture(scope="module", autouse=True)
def PaymentTokenGovernorProxyContract(PaymentTokenGovernorContract, accounts):
	yield PaymentTokenGovernorProxy.deploy(PaymentTokenGovernorContract, {'from': accounts[0]})

@pytest.fixture(scope="module")
def FeeGovernorContract(FeeGovernor, accounts):
	yield FeeGovernor.deploy(1e8, {'from': accounts[0]})

@pytest.fixture(scope="module")
def FeeGovernorProxyContract(FeeGovernorContract, FeeGovernorProxy, accounts):
	yield FeeGovernorProxy.deploy(FeeGovernorContract, {'from': accounts[0]})

@pytest.fixture(scope="module")
def FDTMultiERC20WithFeeContract(FundsDistributionTokenMultiERC20WithFee, accounts):
	yield FundsDistributionTokenMultiERC20WithFee.deploy({'from': accounts[0]})

@pytest.fixture(scope="module")
def FDTMultiERC20FactoryContract(
	PaymentTokenGovernorProxyContract,
	FeeGovernorProxyContract,
	FDTMultiERC20WithFeeContract,
	FundsDistributionTokenERC20Factory,
	accounts
):
	yield FundsDistributionTokenMultiERC20WithFeeFactory.deploy(
		FundsDistributionTokenMultiERC20WithFee[0].address,
		accounts[0],
		PaymentTokenGovernorProxyContract.address,
		FeeGovernorProxyContract.address,
		{'from': accounts[0]}
	)

@pytest.fixture(scope="module", autouse=True)
def test_deploy_fdt_from_factory(FDTMultiERC20FactoryContract, accounts):

	tx1 = FDTMultiERC20FactoryContract.deploy_fdt_contract(TOKEN_NAME, TOKEN_SYMBOL, TOKEN_DECIMALS, TOKEN_SUPPLY, {'from': accounts[0]})

	global FDT_INSTANCE
	FDT_INSTANCE = tx1.new_contracts[0]

@pytest.fixture(scope="module", autouse=True)
def add_payment_token_to_first_governor(PaymentTokenGovernorContract, PaymentToken, accounts):

	tx1 = PaymentTokenGovernorContract.add_payment_token(PaymentToken, {'from': accounts[0]})

@pytest.fixture(scope="module", autouse=True)
def add_new_payment_token_to_second_governor(NewPaymentTokenGovernorContract, NewPaymentToken, accounts):

	tx1 = NewPaymentTokenGovernorContract.add_payment_token(NewPaymentToken, {'from': accounts[0]})

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
	pass

def test_initial_state(accounts):

	fdt_instance = FundsDistributionTokenMultiERC20WithFee.at(FDT_INSTANCE)

	assert fdt_instance.balanceOf(accounts[0]) == 100
	assert fdt_instance.balanceOf(accounts[1]) == 0

def test_unregistered_payment_token(NewPaymentToken, accounts):
	"""
	Address pays with unregistered payment token
	"""
	fdt_instance = FundsDistributionTokenMultiERC20WithFee.at(FDT_INSTANCE)
	tx1_1 = NewPaymentToken.approve(fdt_instance, 500e18, {'from': accounts[0]})

	with reverts():
		tx1_2 = fdt_instance.payToContract(500e18, NewPaymentToken, {'from': accounts[0]})

def test_same_IO(PaymentToken, PaymentTokenGovernorContract, accounts):

	"""
		Address with 100 tokens pays to contract, and withdraws
	"""

	fdt_instance = FundsDistributionTokenMultiERC20WithFee.at(FDT_INSTANCE)
	tx1_1 = PaymentToken.approve(fdt_instance, 500e18, {'from': accounts[0]})

	tx1_2 = fdt_instance.payToContract(500e18, PaymentToken, {'from': accounts[0]})

	assert PaymentToken.balanceOf(fdt_instance) == 500e18

	account_balance = PaymentToken.balanceOf(accounts[0])

	tx2 = fdt_instance.updateFundsTokenBalance({'from': accounts[0]})

	assert tx2.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx2.events['FundsDistributed']['paymentToken'] == PaymentToken
	assert fdt_instance.withdrawableFundsOf(accounts[0], PaymentToken) == 495e18

	tx3 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert tx3.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert tx3.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert PaymentToken.balanceOf(fdt_instance) == 5e18
	assert PaymentToken.balanceOf(accounts[0]) == account_balance + 495e18

	tx4 = fdt_instance.withdrawAdminFee({'from': accounts[0]})
	assert PaymentToken.balanceOf(fdt_instance) == 0
	assert tx4.events['AdminFeeWithdrawn']['beneficiary'] == accounts[0]
	assert tx4.events['AdminFeeWithdrawn']['paymentToken'] == PaymentToken
	assert tx4.events['AdminFeeWithdrawn']['value'] == 5e18


def test_different_IO_single_deposit(PaymentToken, accounts):

	"""
		Non-token holding address pays to contract, address with 100 tokens withdraws
	"""
	fdt_instance = FundsDistributionTokenMultiERC20WithFee.at(FDT_INSTANCE)
	tx0 = PaymentToken.transfer(accounts[1], 500e18, {'from': accounts[0]})
	tx1_1 = PaymentToken.approve(fdt_instance, 500e18, {'from': accounts[1]})
	tx1_2 = fdt_instance.payToContract(500e18, PaymentToken, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 500e18

	account_balance = PaymentToken.balanceOf(accounts[0])

	tx2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert tx2.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx2.events['FundsDistributed']['paymentToken'] == PaymentToken
	assert tx2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert tx2.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert PaymentToken.balanceOf(fdt_instance) == 5e18
	assert PaymentToken.balanceOf(accounts[0]) == account_balance + 495e18

	account_balance = PaymentToken.balanceOf(accounts[0])

	tx3 = fdt_instance.withdrawAdminFee({'from': accounts[0]})
	assert PaymentToken.balanceOf(fdt_instance) == 0
	assert tx3.events['AdminFeeWithdrawn']['beneficiary'] == accounts[0]
	assert tx3.events['AdminFeeWithdrawn']['paymentToken'] == PaymentToken
	assert tx3.events['AdminFeeWithdrawn']['value'] == 5e18
	assert PaymentToken.balanceOf(accounts[0]) == account_balance + 5e18


def test_two_token_holders_single_deposit(PaymentToken, accounts):

	"""
		Two address with 50 tokens each, withdraws
	"""
	fdt_instance = FundsDistributionTokenMultiERC20WithFee.at(FDT_INSTANCE)
	tx1 = fdt_instance.transfer(accounts[1], 50, {'from': accounts[0]})

	tx2_1 = PaymentToken.transfer(accounts[1], 500e18, {'from': accounts[0]})
	tx2_2 = PaymentToken.approve(fdt_instance, 500e18, {'from': accounts[1]})
	tx2_3 = fdt_instance.payToContract(500e18, PaymentToken, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 500e18

	account_balance = PaymentToken.balanceOf(accounts[0])

	tx3 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert tx3.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx3.events['FundsDistributed']['paymentToken'] == PaymentToken
	assert tx3.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert tx3.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert PaymentToken.balanceOf(fdt_instance) == 252.5e18
	assert PaymentToken.balanceOf(accounts[0]) == account_balance + 247.5e18

	account_balance = PaymentToken.balanceOf(accounts[1])

	tx4 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert tx4.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert tx4.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert PaymentToken.balanceOf(fdt_instance) == 5e18
	assert PaymentToken.balanceOf(accounts[1]) == account_balance + 247.5e18

	account_balance = PaymentToken.balanceOf(accounts[0])

	tx5 = fdt_instance.withdrawAdminFee({'from': accounts[0]})
	assert PaymentToken.balanceOf(fdt_instance) == 0
	assert tx5.events['AdminFeeWithdrawn']['beneficiary'] == accounts[0]
	assert tx5.events['AdminFeeWithdrawn']['paymentToken'] == PaymentToken
	assert tx5.events['AdminFeeWithdrawn']['value'] == 5e18
	assert PaymentToken.balanceOf(accounts[0]) == account_balance + 5e18

def test_three_token_holders_single_deposit(PaymentToken, accounts):
	"""
		Single payer, three addresses withdraws
	"""
	fdt_instance = FundsDistributionTokenMultiERC20WithFee.at(FDT_INSTANCE)
	tx1_1 = fdt_instance.transfer(accounts[1], 25, {'from': accounts[0]})
	tx1_2 = fdt_instance.transfer(accounts[2], 35, {'from': accounts[0]})

	tx2_1 = PaymentToken.transfer(accounts[1], 500e18, {'from': accounts[0]})
	tx2_2 = PaymentToken.approve(fdt_instance, 500e18, {'from': accounts[1]})
	tx2_3 = fdt_instance.payToContract(500e18, PaymentToken, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 500e18

	account1_balance = PaymentToken.balanceOf(accounts[0])

	tx3 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert tx3.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx3.events['FundsDistributed']['paymentToken'] == PaymentToken
	assert tx3.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert tx3.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert PaymentToken.balanceOf(fdt_instance) == 302e18
	assert PaymentToken.balanceOf(accounts[0]) == account1_balance + 198e18

	account2_balance = PaymentToken.balanceOf(accounts[1])

	tx4 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert tx4.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert tx4.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert PaymentToken.balanceOf(fdt_instance) == 178.25e18
	assert PaymentToken.balanceOf(accounts[1]) == account2_balance + 123.75e18

	account3_balance = PaymentToken.balanceOf(accounts[2])

	tx5 = fdt_instance.withdrawFunds({'from': accounts[2]})

	assert tx5.events['FundsWithdrawn']['receiver'] == accounts[2]
	assert tx5.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert PaymentToken.balanceOf(fdt_instance) == 5e18
	assert PaymentToken.balanceOf(accounts[2]) == account3_balance + 173.25e18


def test_different_IO_single_deposit_with_token_transfer(PaymentToken, accounts):

	"""
		Account holding 100 tokens pays to contract, transfers all tokens to another address.
		Both withdraws.
	"""
	fdt_instance = FundsDistributionTokenMultiERC20WithFee.at(FDT_INSTANCE)
	tx1_2 = PaymentToken.approve(fdt_instance, 500e18, {'from': accounts[0]})
	tx1_3 = fdt_instance.payToContract(500e18, PaymentToken, {'from': accounts[0]})

	assert PaymentToken.balanceOf(fdt_instance) == 500e18

	update_tx = fdt_instance.updateFundsTokenBalance({'from': accounts[0]})
	assert update_tx.events['FundsDistributed']['receiver'] == accounts[0]
	assert update_tx.events['FundsDistributed']['paymentToken'] == PaymentToken


	FDT_transfer = fdt_instance.transfer(accounts[1], 100, {'from': accounts[0]})

	assert fdt_instance.balanceOf(accounts[0]) == 0

	account1_balance = PaymentToken.balanceOf(accounts[0])
	account2_balance = PaymentToken.balanceOf(accounts[1])

	account1_withdraw = fdt_instance.withdrawFunds({'from': accounts[0]})


	assert account1_withdraw.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert account1_withdraw.events['FundsWithdrawn']['value'] == 0
	assert PaymentToken.balanceOf(fdt_instance) == 500e18
	assert PaymentToken.balanceOf(accounts[0]) == account1_balance

	account2_withdraw = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 5e18
	assert PaymentToken.balanceOf(accounts[1]) == account2_balance + 495e18


def test_multiple_deposit_with_intervening_transfer_two_withdrawals(PaymentToken, accounts):
	"""
		Two addresses holding tokens.
		One deposit is made.
		One address withdraws.
		Another deposit is made.
		Both addresses withdraw.
	"""
	fdt_instance = FundsDistributionTokenMultiERC20WithFee.at(FDT_INSTANCE)
	FDT_transfer = fdt_instance.transfer(accounts[1], 40, {'from': accounts[0]})

	assert FDT_transfer.events['Transfer']['sender'] == accounts[0]
	assert FDT_transfer.events['Transfer']['receiver'] == accounts[1]
	assert FDT_transfer.events['Transfer']['value'] == 40

	payment1_1 = PaymentToken.transfer(accounts[1], 2000e18, {'from': accounts[0]})
	payment1_2 = PaymentToken.approve(fdt_instance, 2000e18, {'from': accounts[1]})
	payment1_3 = fdt_instance.payToContract(1000e18, PaymentToken, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 1000e18

	account1_balance1 = PaymentToken.balanceOf(accounts[0])

	account1_withdraw1 = fdt_instance.withdrawFunds({'from': accounts[0]})
	assert account1_withdraw1.events['FundsDistributed']['receiver'] == accounts[0]
	assert account1_withdraw1.events['FundsDistributed']['paymentToken'] == PaymentToken
	assert account1_withdraw1.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw1.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert account1_withdraw1.events['FundsWithdrawn']['value'] == 594e18
	assert PaymentToken.balanceOf(fdt_instance) == 406e18
	assert PaymentToken.balanceOf(accounts[0]) == account1_balance1 + 594e18
	assert fdt_instance.payment_token_to_admin_fee_balance(PaymentToken) == 10e18

	payment2_1 = PaymentToken.approve(fdt_instance, 1000e18, {'from': accounts[1]})
	payment2_1 = fdt_instance.payToContract(1000e18, PaymentToken, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 1406e18

	account2_balance = PaymentToken.balanceOf(accounts[1])

	update_tx = fdt_instance.updateFundsTokenBalance({'from': accounts[0]})
	assert update_tx.events['FundsDistributed']['receiver'] == accounts[0]
	assert update_tx.events['FundsDistributed']['paymentToken'] == PaymentToken
	assert update_tx.events['FundsDistributed']['value'] == 1000e18
	assert fdt_instance.payment_token_to_admin_fee_balance(PaymentToken) == 20e18

	account2_withdraw1 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert account2_withdraw1.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert account2_withdraw1.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert account2_withdraw1.events['FundsWithdrawn']['value'] == 792e18
	assert PaymentToken.balanceOf(fdt_instance) == 614e18
	assert PaymentToken.balanceOf(accounts[1]) == account2_balance + 792e18


	account1_balance2 = PaymentToken.balanceOf(accounts[0])

	account1_withdraw2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert account1_withdraw2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw2.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert account1_withdraw2.events['FundsWithdrawn']['value'] == 594e18
	assert PaymentToken.balanceOf(fdt_instance) == 20e18
	assert PaymentToken.balanceOf(accounts[0]) == account1_balance2 + 594e18


def test_multiple_deposit_lower_value_with_intervening_transfer_two_withdrawals(PaymentToken, accounts):
	"""
		Two addresses holding tokens.
		One deposit is made.
		One address withdraws.
		Another deposit is made that results in contract balance < first deposit.
		Both addresses withdraw.
	"""
	fdt_instance = FundsDistributionTokenMultiERC20WithFee.at(FDT_INSTANCE)
	FDT_transfer = fdt_instance.transfer(accounts[1], 40, {'from': accounts[0]})

	assert FDT_transfer.events['Transfer']['sender'] == accounts[0]
	assert FDT_transfer.events['Transfer']['receiver'] == accounts[1]
	assert FDT_transfer.events['Transfer']['value'] == 40

	payment1_1 = PaymentToken.transfer(accounts[1], 10000e18, {'from': accounts[0]})
	payment1_2 = PaymentToken.approve(fdt_instance, 10000e18, {'from': accounts[1]})
	payment1_3 = fdt_instance.payToContract(5000e18, PaymentToken, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 5000e18

	account1_balance1 = PaymentToken.balanceOf(accounts[0])

	account1_withdraw1 = fdt_instance.withdrawFunds({'from': accounts[0]})
	assert account1_withdraw1.events['FundsDistributed']['receiver'] == accounts[0]
	assert account1_withdraw1.events['FundsDistributed']['paymentToken'] == PaymentToken
	assert account1_withdraw1.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw1.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert account1_withdraw1.events['FundsWithdrawn']['value'] == 2970e18
	assert PaymentToken.balanceOf(fdt_instance) == 2030e18
	assert PaymentToken.balanceOf(accounts[0]) == account1_balance1 + 2970e18
	assert fdt_instance.payment_token_to_admin_fee_balance(PaymentToken) == 50e18


	payment1 = fdt_instance.payToContract(1000e18, PaymentToken, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 3030e18

	account2_balance = PaymentToken.balanceOf(accounts[1])

	update_tx = fdt_instance.updateFundsTokenBalance({'from': accounts[0]})
	assert update_tx.events['FundsDistributed']['receiver'] == accounts[0]
	assert update_tx.events['FundsDistributed']['paymentToken'] == PaymentToken
	assert update_tx.events['FundsDistributed']['value'] == 1000e18
	assert fdt_instance.payment_token_to_admin_fee_balance(PaymentToken) == 60e18

	account2_withdraw1 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert account2_withdraw1.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert account2_withdraw1.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert account2_withdraw1.events['FundsWithdrawn']['value'] == 2376e18
	assert PaymentToken.balanceOf(fdt_instance) == 654e18
	assert PaymentToken.balanceOf(accounts[1]) == account2_balance + 2376e18


	account1_balance2 = PaymentToken.balanceOf(accounts[0])

	account1_withdraw2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert account1_withdraw2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw2.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert account1_withdraw2.events['FundsWithdrawn']['value'] == 594e18
	assert PaymentToken.balanceOf(fdt_instance) == 60e18
	assert PaymentToken.balanceOf(accounts[0]) == account1_balance2 + 594e18


def test_same_IO_two_payment_tokens(PaymentToken, NewPaymentToken, PaymentTokenGovernorContract, accounts):

	"""
		Address with 100 tokens pays to contract, and withdraws
	"""

	fdt_instance = FundsDistributionTokenMultiERC20WithFee.at(FDT_INSTANCE)
	tx1_1 = PaymentToken.approve(fdt_instance, 500e18, {'from': accounts[0]})

	tx1_2 = fdt_instance.payToContract(500e18, PaymentToken, {'from': accounts[0]})

	assert PaymentToken.balanceOf(fdt_instance) == 500e18

	PaymentTokenGovernorContract.add_payment_token(NewPaymentToken, {'from': accounts[0]})
	tx1_3 = NewPaymentToken.approve(fdt_instance, 1000e18, {'from': accounts[0]})
	tx1_4 = fdt_instance.payToContract(1000e18, NewPaymentToken, {'from': accounts[0]})


	account_payment_token_balance = PaymentToken.balanceOf(accounts[0])
	account1_new_payment_token_balance = NewPaymentToken.balanceOf(accounts[0])

	tx2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert len(tx2.events['FundsDistributed']) == 2
	assert tx2.events['FundsDistributed'][0]['receiver'] == accounts[0]
	assert tx2.events['FundsDistributed'][0]['paymentToken'] == PaymentToken
	assert tx2.events['FundsDistributed'][0]['value'] == 500e18
	assert fdt_instance.payment_token_to_admin_fee_balance(PaymentToken) == 5e18
	assert tx2.events['FundsDistributed'][1]['receiver'] == accounts[0]
	assert tx2.events['FundsDistributed'][1]['paymentToken'] == NewPaymentToken
	assert tx2.events['FundsDistributed'][1]['value'] == 1000e18
	assert fdt_instance.payment_token_to_admin_fee_balance(NewPaymentToken) == 10e18

	assert len(tx2.events['FundsWithdrawn']) == 2
	assert tx2.events['FundsWithdrawn'][0]['receiver'] == accounts[0]
	assert tx2.events['FundsWithdrawn'][0]['paymentToken'] == PaymentToken
	assert tx2.events['FundsWithdrawn'][0]['value'] == 495e18
	assert tx2.events['FundsWithdrawn'][1]['receiver'] == accounts[0]
	assert tx2.events['FundsWithdrawn'][1]['paymentToken'] == NewPaymentToken
	assert tx2.events['FundsWithdrawn'][1]['value'] == 990e18

	assert PaymentToken.balanceOf(fdt_instance) == 5e18
	assert PaymentToken.balanceOf(accounts[0]) == account_payment_token_balance + 495e18

	assert NewPaymentToken.balanceOf(fdt_instance) == 10e18
	assert NewPaymentToken.balanceOf(accounts[0]) == account1_new_payment_token_balance + 990e18

	account_payment_token_balance = PaymentToken.balanceOf(accounts[0])
	account1_new_payment_token_balance = NewPaymentToken.balanceOf(accounts[0])

	withdraw_admin_fee = fdt_instance.withdrawAdminFee({'from': accounts[0]})

	assert len(withdraw_admin_fee.events['AdminFeeWithdrawn']) == 2
	assert withdraw_admin_fee.events['AdminFeeWithdrawn'][0]['beneficiary'] == accounts[0]
	assert withdraw_admin_fee.events['AdminFeeWithdrawn'][0]['paymentToken'] == PaymentToken
	assert withdraw_admin_fee.events['AdminFeeWithdrawn'][0]['value'] == 5e18
	assert PaymentToken.balanceOf(fdt_instance) == 0
	assert PaymentToken.balanceOf(accounts[0]) == account_payment_token_balance + 5e18

	assert withdraw_admin_fee.events['AdminFeeWithdrawn'][1]['beneficiary'] == accounts[0]
	assert withdraw_admin_fee.events['AdminFeeWithdrawn'][1]['paymentToken'] == NewPaymentToken
	assert withdraw_admin_fee.events['AdminFeeWithdrawn'][1]['value'] == 10e18
	assert NewPaymentToken.balanceOf(fdt_instance) == 0
	assert NewPaymentToken.balanceOf(accounts[0]) == account1_new_payment_token_balance + 10e18

def test_multiple_deposit_with_two_payment_tokens_and_intervening_transfer_two_withdrawals(PaymentToken, NewPaymentToken, PaymentTokenGovernorContract, accounts):
	"""
		Two addresses holding tokens.
		One deposit is made using Payment Token.
		One address withdraws.
		Another deposit is made using Payment Token.
		Another deposit is made using New Payment Token
		Both addresses withdraw.
	"""
	fdt_instance = FundsDistributionTokenMultiERC20WithFee.at(FDT_INSTANCE)
	FDT_transfer = fdt_instance.transfer(accounts[1], 40, {'from': accounts[0]})

	assert FDT_transfer.events['Transfer']['sender'] == accounts[0]
	assert FDT_transfer.events['Transfer']['receiver'] == accounts[1]
	assert FDT_transfer.events['Transfer']['value'] == 40

	payment1_1 = PaymentToken.transfer(accounts[1], 2000e18, {'from': accounts[0]})
	payment1_2 = PaymentToken.approve(fdt_instance, 2000e18, {'from': accounts[1]})
	payment1_3 = fdt_instance.payToContract(1000e18, PaymentToken, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 1000e18

	account1_balance1 = PaymentToken.balanceOf(accounts[0])

	account1_withdraw1 = fdt_instance.withdrawFunds({'from': accounts[0]})
	assert account1_withdraw1.events['FundsDistributed']['receiver'] == accounts[0]
	assert account1_withdraw1.events['FundsDistributed']['paymentToken'] == PaymentToken
	assert account1_withdraw1.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw1.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert account1_withdraw1.events['FundsWithdrawn']['value'] == 594e18
	assert PaymentToken.balanceOf(fdt_instance) == 406e18
	assert PaymentToken.balanceOf(accounts[0]) == account1_balance1 + 594e18
	assert fdt_instance.payment_token_to_admin_fee_balance(PaymentToken) == 10e18

	PaymentTokenGovernorContract.add_payment_token(NewPaymentToken, {'from': accounts[0]})

	payment2_1 = PaymentToken.approve(fdt_instance, 1000e18, {'from': accounts[1]})
	payment2_2 = fdt_instance.payToContract(1000e18, PaymentToken, {'from': accounts[1]})
	payment2_3 = NewPaymentToken.approve(fdt_instance, 2000e18, {'from': accounts[0]})
	payment2_4 = fdt_instance.payToContract(2000e18, NewPaymentToken, {'from': accounts[0]})

	assert PaymentToken.balanceOf(fdt_instance) == 1406e18
	assert NewPaymentToken.balanceOf(fdt_instance) == 2000e18

	account2_payment_token_balance = PaymentToken.balanceOf(accounts[1])
	account2_new_payment_token_balance = NewPaymentToken.balanceOf(accounts[1])

	update_tx = fdt_instance.updateFundsTokenBalance({'from': accounts[0]})
	assert len(update_tx.events) == 2
	assert update_tx.events['FundsDistributed'][0]['receiver'] == accounts[0]
	assert update_tx.events['FundsDistributed'][0]['paymentToken'] == PaymentToken
	assert update_tx.events['FundsDistributed'][0]['value'] == 1000e18
	assert fdt_instance.payment_token_to_admin_fee_balance(PaymentToken) == 20e18

	assert update_tx.events['FundsDistributed'][1]['receiver'] == accounts[0]
	assert update_tx.events['FundsDistributed'][1]['paymentToken'] == NewPaymentToken
	assert update_tx.events['FundsDistributed'][1]['value'] == 2000e18
	assert fdt_instance.payment_token_to_admin_fee_balance(NewPaymentToken) == 20e18

	account2_withdraw1 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert len(account2_withdraw1.events['FundsWithdrawn']) == 2
	assert account2_withdraw1.events['FundsWithdrawn'][0]['receiver'] == accounts[1]
	assert account2_withdraw1.events['FundsWithdrawn'][0]['paymentToken'] == PaymentToken
	assert account2_withdraw1.events['FundsWithdrawn'][0]['value'] == 792e18
	assert PaymentToken.balanceOf(fdt_instance) == 614e18
	assert PaymentToken.balanceOf(accounts[1]) == account2_payment_token_balance + 792e18

	assert account2_withdraw1.events['FundsWithdrawn'][1]['receiver'] == accounts[1]
	assert account2_withdraw1.events['FundsWithdrawn'][1]['paymentToken'] == NewPaymentToken
	assert account2_withdraw1.events['FundsWithdrawn'][1]['value'] == 792e18
	assert NewPaymentToken.balanceOf(fdt_instance) == 1208e18
	assert NewPaymentToken.balanceOf(accounts[1]) == account2_new_payment_token_balance + 792e18


	account1_payment_token_balance_2 = PaymentToken.balanceOf(accounts[0])
	account1_new_payment_token_balance = NewPaymentToken.balanceOf(accounts[0])

	account1_withdraw2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert len(account1_withdraw2.events['FundsWithdrawn']) == 2
	assert account1_withdraw2.events['FundsWithdrawn'][0]['receiver'] == accounts[0]
	assert account1_withdraw2.events['FundsWithdrawn'][0]['paymentToken'] == PaymentToken
	assert account1_withdraw2.events['FundsWithdrawn'][0]['value'] == 594e18
	assert PaymentToken.balanceOf(fdt_instance) == 20e18
	assert PaymentToken.balanceOf(accounts[0]) == account1_payment_token_balance_2 + 594e18

	assert account1_withdraw2.events['FundsWithdrawn'][1]['receiver'] == accounts[0]
	assert account1_withdraw2.events['FundsWithdrawn'][1]['paymentToken'] == NewPaymentToken
	assert account1_withdraw2.events['FundsWithdrawn'][1]['value'] == 1188e18
	assert NewPaymentToken.balanceOf(fdt_instance) == 20e18
	assert NewPaymentToken.balanceOf(accounts[0]) == account1_new_payment_token_balance + 1188e18

	account_payment_token_balance = PaymentToken.balanceOf(accounts[0])
	account1_new_payment_token_balance = NewPaymentToken.balanceOf(accounts[0])

	withdraw_admin_fee = fdt_instance.withdrawAdminFee({'from': accounts[0]})

	assert len(withdraw_admin_fee.events['AdminFeeWithdrawn']) == 2
	assert withdraw_admin_fee.events['AdminFeeWithdrawn'][0]['beneficiary'] == accounts[0]
	assert withdraw_admin_fee.events['AdminFeeWithdrawn'][0]['paymentToken'] == PaymentToken
	assert withdraw_admin_fee.events['AdminFeeWithdrawn'][0]['value'] == 20e18
	assert PaymentToken.balanceOf(fdt_instance) == 0
	assert PaymentToken.balanceOf(accounts[0]) == account_payment_token_balance + 20e18

	assert withdraw_admin_fee.events['AdminFeeWithdrawn'][1]['beneficiary'] == accounts[0]
	assert withdraw_admin_fee.events['AdminFeeWithdrawn'][1]['paymentToken'] == NewPaymentToken
	assert withdraw_admin_fee.events['AdminFeeWithdrawn'][1]['value'] == 20e18
	assert NewPaymentToken.balanceOf(fdt_instance) == 0
	assert NewPaymentToken.balanceOf(accounts[0]) == account1_new_payment_token_balance + 20e18

def test_payment_to_first_governor_and_switch_governor(PaymentToken, NewPaymentToken, PaymentTokenGovernorProxyContract, NewPaymentTokenGovernorContract, accounts):
	"""
		One address holds 100 FDT.
		One payment is made based on 1st payment token under 1st governor contract
		Governor contract is changed
		Another payment is made based on 2nd payment token under 2nd governor contract
		Funds are distributed for 2nd payment token only
	"""

	fdt_instance = FundsDistributionTokenMultiERC20WithFee.at(FDT_INSTANCE)
	FDT_transfer = fdt_instance.transfer(accounts[1], 40, {'from': accounts[0]})

	assert FDT_transfer.events['Transfer']['sender'] == accounts[0]
	assert FDT_transfer.events['Transfer']['receiver'] == accounts[1]
	assert FDT_transfer.events['Transfer']['value'] == 40

	payment1_1 = PaymentToken.transfer(accounts[1], 10000e18, {'from': accounts[0]})
	payment1_2 = PaymentToken.approve(fdt_instance, 10000e18, {'from': accounts[1]})
	payment1_3 = fdt_instance.payToContract(5000e18, PaymentToken, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 5000e18

	# Change payment token governor
	PaymentTokenGovernorProxyContract.commit_change_payment_token_governor(NewPaymentTokenGovernorContract, {'from': accounts[0]})
	chain.sleep(259200)
	PaymentTokenGovernorProxyContract.apply_change_payment_token_governor({'from': accounts[0]})

	assert PaymentTokenGovernorProxyContract.get_payment_token_acceptance(PaymentToken) == False
	assert PaymentTokenGovernorProxyContract.get_payment_token_acceptance(NewPaymentToken) == True
	assert PaymentTokenGovernorProxyContract.get_accepted_payment_token_count() == 1
	assert PaymentTokenGovernorProxyContract.get_accepted_payment_tokens(1) == NewPaymentToken
	assert PaymentTokenGovernorProxyContract.get_accepted_payment_tokens(2) == ZERO_ADDRESS

	# Make payment in 2nd payment token

	payment2_1 = NewPaymentToken.approve(fdt_instance, 10000e18, {'from': accounts[0]})
	payment2_2 = fdt_instance.payToContract(5000e18, NewPaymentToken, {'from': accounts[0]})

	assert PaymentToken.balanceOf(fdt_instance) == 5000e18

	update_tx = fdt_instance.updateFundsTokenBalance({'from': accounts[0]})
	assert len(update_tx.events) == 1
	assert update_tx.events['FundsDistributed']['receiver'] == accounts[0]
	assert update_tx.events['FundsDistributed']['paymentToken'] == NewPaymentToken
	assert update_tx.events['FundsDistributed']['value'] == 5000e18

	account1_payment_token_balance = PaymentToken.balanceOf(accounts[0])
	account1_new_payment_token_balance = NewPaymentToken.balanceOf(accounts[0])
	account1_withdraw = fdt_instance.withdrawFunds({'from': accounts[0]})

	#assert len(account1_withdraw.events) ==1
	assert account1_withdraw.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw.events['FundsWithdrawn']['paymentToken'] == NewPaymentToken
	assert account1_withdraw.events['FundsWithdrawn']['value'] == 2970e18
	assert NewPaymentToken.balanceOf(fdt_instance) == 2030e18
	assert NewPaymentToken.balanceOf(accounts[0]) == account1_new_payment_token_balance + 2970e18

	assert PaymentToken.balanceOf(fdt_instance) == 5000e18
	assert PaymentToken.balanceOf(accounts[0]) == account1_payment_token_balance
