import pytest

from brownie import (
	accounts,
	reverts,
	ERC20,
	PaymentTokenGovernor,
	PaymentTokenGovernorProxy,
	FundsDistributionTokenMultiERC20,
	FundsDistributionTokenMultiERC20Factory,
)

PAYMENT_TOKEN_NAME = "Sai"
PAYMENT_TOKEN_SYMBOL = "SAI"
PAYMENT_TOKEN_DECIMALS = 18
PAYMENT_TOKEN_SUPPLY = 1000

NEW_PAYMENT_TOKEN_NAME = "Dai"
NEW_PAYMENT_TOKEN_SYMBOL = "DAI"
NEW_PAYMENT_TOKEN_DECIMALS = 18
NEW_PAYMENT_TOKEN_SUPPLY = 1000

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
def FDTMultiERC20Contract(FundsDistributionTokenMultiERC20, accounts):
	yield FundsDistributionTokenMultiERC20.deploy({'from': accounts[0]})

@pytest.fixture(scope="module")
def FDTMultiERC20FactoryContract(PaymentTokenGovernorProxyContract, FDTMultiERC20Contract, FundsDistributionTokenERC20Factory, accounts):
	yield FundsDistributionTokenMultiERC20Factory.deploy(FundsDistributionTokenMultiERC20[0].address, accounts[0], PaymentTokenGovernorProxyContract.address, {'from': accounts[0]})

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

	fdt_instance = FundsDistributionTokenMultiERC20.at(FDT_INSTANCE)

	assert fdt_instance.balanceOf(accounts[0]) == 100
	assert fdt_instance.balanceOf(accounts[1]) == 0

def test_unregistered_payment_token(NewPaymentToken, accounts):
	"""
	Address pays with unregistered payment token
	"""
	fdt_instance = FundsDistributionTokenMultiERC20.at(FDT_INSTANCE)
	tx1_1 = NewPaymentToken.approve(fdt_instance, 500, {'from': accounts[0]})

	with reverts():
		tx1_2 = fdt_instance.payToContract(500, NewPaymentToken, {'from': accounts[0]})

def test_same_IO(PaymentToken, PaymentTokenGovernorContract, accounts):

	"""
		Address with 100 tokens pays to contract, and withdraws
	"""

	fdt_instance = FundsDistributionTokenMultiERC20.at(FDT_INSTANCE)
	tx1_1 = PaymentToken.approve(fdt_instance, 500, {'from': accounts[0]})

	tx1_2 = fdt_instance.payToContract(500, PaymentToken, {'from': accounts[0]})

	assert PaymentToken.balanceOf(fdt_instance) == 500

	account_balance = PaymentToken.balanceOf(accounts[0])

	tx2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert tx2.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx2.events['FundsDistributed']['paymentToken'] == PaymentToken
	assert tx2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert tx2.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert PaymentToken.balanceOf(fdt_instance) == 0
	assert PaymentToken.balanceOf(accounts[0]) == account_balance + 500

def test_different_IO_single_deposit(PaymentToken, accounts):

	"""
		Non-token holding address pays to contract, address with 100 tokens withdraws
	"""
	fdt_instance = FundsDistributionTokenMultiERC20.at(FDT_INSTANCE)
	tx0 = PaymentToken.transfer(accounts[1], 500, {'from': accounts[0]})
	tx1_1 = PaymentToken.approve(fdt_instance, 500, {'from': accounts[1]})
	tx1_2 = fdt_instance.payToContract(500, PaymentToken, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 500

	account_balance = PaymentToken.balanceOf(accounts[0])

	tx2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert tx2.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx2.events['FundsDistributed']['paymentToken'] == PaymentToken
	assert tx2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert tx2.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert PaymentToken.balanceOf(fdt_instance) == 0
	assert PaymentToken.balanceOf(accounts[0]) == account_balance + 500


def test_two_token_holders_single_deposit(PaymentToken, accounts):

	"""
		Two address with 50 tokens each, withdraws
	"""
	fdt_instance = FundsDistributionTokenMultiERC20.at(FDT_INSTANCE)
	tx1 = fdt_instance.transfer(accounts[1], 50, {'from': accounts[0]})

	tx2_1 = PaymentToken.transfer(accounts[1], 500, {'from': accounts[0]})
	tx2_2 = PaymentToken.approve(fdt_instance, 500, {'from': accounts[1]})
	tx2_3 = fdt_instance.payToContract(500, PaymentToken, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 500

	account_balance = PaymentToken.balanceOf(accounts[0])

	tx3 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert tx3.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx3.events['FundsDistributed']['paymentToken'] == PaymentToken
	assert tx3.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert tx3.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert PaymentToken.balanceOf(fdt_instance) == 250
	assert PaymentToken.balanceOf(accounts[0]) == account_balance + 250

	account_balance = PaymentToken.balanceOf(accounts[1])

	tx4 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert tx4.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert tx4.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert PaymentToken.balanceOf(fdt_instance) == 0
	assert PaymentToken.balanceOf(accounts[1]) == account_balance + 250

def test_three_token_holders_single_deposit(PaymentToken, accounts):
	"""
		Single payer, three addresses withdraws
	"""
	fdt_instance = FundsDistributionTokenMultiERC20.at(FDT_INSTANCE)
	tx1_1 = fdt_instance.transfer(accounts[1], 25, {'from': accounts[0]})
	tx1_2 = fdt_instance.transfer(accounts[2], 35, {'from': accounts[0]})

	tx2_1 = PaymentToken.transfer(accounts[1], 500, {'from': accounts[0]})
	tx2_2 = PaymentToken.approve(fdt_instance, 500, {'from': accounts[1]})
	tx2_3 = fdt_instance.payToContract(500, PaymentToken, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 500

	account1_balance = PaymentToken.balanceOf(accounts[0])

	tx3 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert tx3.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx3.events['FundsDistributed']['paymentToken'] == PaymentToken
	assert tx3.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert tx3.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert PaymentToken.balanceOf(fdt_instance) == 300
	assert PaymentToken.balanceOf(accounts[0]) == account1_balance + 200

	account2_balance = PaymentToken.balanceOf(accounts[1])

	tx4 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert tx4.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert tx4.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert PaymentToken.balanceOf(fdt_instance) == 175
	assert PaymentToken.balanceOf(accounts[1]) == account2_balance + 125

	account3_balance = PaymentToken.balanceOf(accounts[2])

	tx5 = fdt_instance.withdrawFunds({'from': accounts[2]})

	assert tx5.events['FundsWithdrawn']['receiver'] == accounts[2]
	assert tx5.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert PaymentToken.balanceOf(fdt_instance) == 0
	assert PaymentToken.balanceOf(accounts[2]) == account3_balance + 175

def test_different_IO_single_deposit_with_token_transfer(PaymentToken, accounts):

	"""
		Account holding 100 tokens pays to contract, transfers all tokens to another address.
		Both withdraws.
	"""
	fdt_instance = FundsDistributionTokenMultiERC20.at(FDT_INSTANCE)
	tx1_2 = PaymentToken.approve(fdt_instance, 500, {'from': accounts[0]})
	tx1_3 = fdt_instance.payToContract(500, PaymentToken, {'from': accounts[0]})

	assert PaymentToken.balanceOf(fdt_instance) == 500

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
	assert PaymentToken.balanceOf(fdt_instance) == 500
	assert PaymentToken.balanceOf(accounts[0]) == account1_balance

	account2_withdraw = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 0
	assert PaymentToken.balanceOf(accounts[1]) == account2_balance + 500

def test_multiple_deposit_with_intervening_transfer_two_withdrawals(PaymentToken, accounts):
	"""
		Two addresses holding tokens.
		One deposit is made.
		One address withdraws.
		Another deposit is made.
		Both addresses withdraw.
	"""
	fdt_instance = FundsDistributionTokenMultiERC20.at(FDT_INSTANCE)
	FDT_transfer = fdt_instance.transfer(accounts[1], 40, {'from': accounts[0]})

	assert FDT_transfer.events['Transfer']['sender'] == accounts[0]
	assert FDT_transfer.events['Transfer']['receiver'] == accounts[1]
	assert FDT_transfer.events['Transfer']['value'] == 40

	payment1_1 = PaymentToken.transfer(accounts[1], 2000, {'from': accounts[0]})
	payment1_2 = PaymentToken.approve(fdt_instance, 2000, {'from': accounts[1]})
	payment1_3 = fdt_instance.payToContract(1000, PaymentToken, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 1000

	account1_balance1 = PaymentToken.balanceOf(accounts[0])

	account1_withdraw1 = fdt_instance.withdrawFunds({'from': accounts[0]})
	assert account1_withdraw1.events['FundsDistributed']['receiver'] == accounts[0]
	assert account1_withdraw1.events['FundsDistributed']['paymentToken'] == PaymentToken
	assert account1_withdraw1.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw1.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert account1_withdraw1.events['FundsWithdrawn']['value'] == 600
	assert PaymentToken.balanceOf(fdt_instance) == 400
	assert PaymentToken.balanceOf(accounts[0]) == account1_balance1 + 600

	payment2_1 = PaymentToken.approve(fdt_instance, 1000, {'from': accounts[1]})
	payment2_1 = fdt_instance.payToContract(1000, PaymentToken, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 1400

	account2_balance = PaymentToken.balanceOf(accounts[1])

	update_tx = fdt_instance.updateFundsTokenBalance({'from': accounts[0]})
	assert update_tx.events['FundsDistributed']['receiver'] == accounts[0]
	assert update_tx.events['FundsDistributed']['paymentToken'] == PaymentToken
	assert update_tx.events['FundsDistributed']['value'] == 1000


	account2_withdraw1 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert account2_withdraw1.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert account2_withdraw1.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert account2_withdraw1.events['FundsWithdrawn']['value'] == 800
	assert PaymentToken.balanceOf(fdt_instance) == 600
	assert PaymentToken.balanceOf(accounts[1]) == account2_balance + 800


	account1_balance2 = PaymentToken.balanceOf(accounts[0])

	account1_withdraw2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert account1_withdraw2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw2.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert account1_withdraw2.events['FundsWithdrawn']['value'] == 600
	assert PaymentToken.balanceOf(fdt_instance) == 0
	assert PaymentToken.balanceOf(accounts[0]) == account1_balance2 + 600

def test_multiple_deposit_lower_value_with_intervening_transfer_two_withdrawals(PaymentToken, accounts):
	"""
		Two addresses holding tokens.
		One deposit is made.
		One address withdraws.
		Another deposit is made that results in contract balance < first deposit.
		Both addresses withdraw.
	"""
	fdt_instance = FundsDistributionTokenMultiERC20.at(FDT_INSTANCE)
	FDT_transfer = fdt_instance.transfer(accounts[1], 40, {'from': accounts[0]})

	assert FDT_transfer.events['Transfer']['sender'] == accounts[0]
	assert FDT_transfer.events['Transfer']['receiver'] == accounts[1]
	assert FDT_transfer.events['Transfer']['value'] == 40

	payment1_1 = PaymentToken.transfer(accounts[1], 10000, {'from': accounts[0]})
	payment1_2 = PaymentToken.approve(fdt_instance, 10000, {'from': accounts[1]})
	payment1_3 = fdt_instance.payToContract(5000, PaymentToken, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 5000

	account1_balance1 = PaymentToken.balanceOf(accounts[0])

	account1_withdraw1 = fdt_instance.withdrawFunds({'from': accounts[0]})
	assert account1_withdraw1.events['FundsDistributed']['receiver'] == accounts[0]
	assert account1_withdraw1.events['FundsDistributed']['paymentToken'] == PaymentToken
	assert account1_withdraw1.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw1.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert account1_withdraw1.events['FundsWithdrawn']['value'] == 3000
	assert PaymentToken.balanceOf(fdt_instance) == 2000
	assert PaymentToken.balanceOf(accounts[0]) == account1_balance1 + 3000


	payment1 = fdt_instance.payToContract(1000, PaymentToken, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 3000

	account2_balance = PaymentToken.balanceOf(accounts[1])

	update_tx = fdt_instance.updateFundsTokenBalance({'from': accounts[0]})
	assert update_tx.events['FundsDistributed']['receiver'] == accounts[0]
	assert update_tx.events['FundsDistributed']['paymentToken'] == PaymentToken
	assert update_tx.events['FundsDistributed']['value'] == 1000

	account2_withdraw1 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert account2_withdraw1.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert account2_withdraw1.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert account2_withdraw1.events['FundsWithdrawn']['value'] == 2400
	assert PaymentToken.balanceOf(fdt_instance) == 600
	assert PaymentToken.balanceOf(accounts[1]) == account2_balance + 2400


	account1_balance2 = PaymentToken.balanceOf(accounts[0])

	account1_withdraw2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert account1_withdraw2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw2.events['FundsWithdrawn']['paymentToken'] == PaymentToken
	assert account1_withdraw2.events['FundsWithdrawn']['value'] == 600
	assert PaymentToken.balanceOf(fdt_instance) == 0
	assert PaymentToken.balanceOf(accounts[0]) == account1_balance2 + 600

def test_same_IO_two_payment_tokens(PaymentToken, NewPaymentToken, PaymentTokenGovernorContract, accounts):

	"""
		Address with 100 tokens pays to contract, and withdraws
	"""

	fdt_instance = FundsDistributionTokenMultiERC20.at(FDT_INSTANCE)
	tx1_1 = PaymentToken.approve(fdt_instance, 500, {'from': accounts[0]})

	tx1_2 = fdt_instance.payToContract(500, PaymentToken, {'from': accounts[0]})

	assert PaymentToken.balanceOf(fdt_instance) == 500

	PaymentTokenGovernorContract.add_payment_token(NewPaymentToken, {'from': accounts[0]})
	tx1_3 = NewPaymentToken.approve(fdt_instance, 1000, {'from': accounts[0]})
	tx1_4 = fdt_instance.payToContract(1000, NewPaymentToken, {'from': accounts[0]})


	account_payment_token_balance = PaymentToken.balanceOf(accounts[0])
	account1_new_payment_token_balance = NewPaymentToken.balanceOf(accounts[0])

	tx2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert len(tx2.events['FundsDistributed']) == 2
	assert tx2.events['FundsDistributed'][0]['receiver'] == accounts[0]
	assert tx2.events['FundsDistributed'][0]['paymentToken'] == PaymentToken
	assert tx2.events['FundsDistributed'][0]['value'] == 500
	assert tx2.events['FundsDistributed'][1]['receiver'] == accounts[0]
	assert tx2.events['FundsDistributed'][1]['paymentToken'] == NewPaymentToken
	assert tx2.events['FundsDistributed'][1]['value'] == 1000

	assert len(tx2.events['FundsWithdrawn']) == 2
	assert tx2.events['FundsWithdrawn'][0]['receiver'] == accounts[0]
	assert tx2.events['FundsWithdrawn'][0]['paymentToken'] == PaymentToken
	assert tx2.events['FundsWithdrawn'][0]['value'] == 500
	assert tx2.events['FundsWithdrawn'][1]['receiver'] == accounts[0]
	assert tx2.events['FundsWithdrawn'][1]['paymentToken'] == NewPaymentToken
	assert tx2.events['FundsWithdrawn'][1]['value'] == 1000

	assert PaymentToken.balanceOf(fdt_instance) == 0
	assert PaymentToken.balanceOf(accounts[0]) == account_payment_token_balance + 500

	assert NewPaymentToken.balanceOf(fdt_instance) == 0
	assert PaymentToken.balanceOf(accounts[0]) == account1_new_payment_token_balance + 1000

def test_payment_to_first_governor_and_switch_governor(PaymentToken, NewPaymentToken, PaymentTokenGovernorProxyContract, NewPaymentTokenGovernorContract, accounts):
	"""
		One address holds 100 FDT.
		One payment is made based on 1st payment token under 1st governor contract
		Governor contract is changed
		Another payment is made based on 2nd payment token under 2nd governor contract
		Funds are distributed for 2nd payment token only
	"""

	fdt_instance = FundsDistributionTokenMultiERC20.at(FDT_INSTANCE)
	FDT_transfer = fdt_instance.transfer(accounts[1], 40, {'from': accounts[0]})

	assert FDT_transfer.events['Transfer']['sender'] == accounts[0]
	assert FDT_transfer.events['Transfer']['receiver'] == accounts[1]
	assert FDT_transfer.events['Transfer']['value'] == 40

	payment1_1 = PaymentToken.transfer(accounts[1], 10000, {'from': accounts[0]})
	payment1_2 = PaymentToken.approve(fdt_instance, 10000, {'from': accounts[1]})
	payment1_3 = fdt_instance.payToContract(5000, PaymentToken, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 5000

	# Change payment token governor
	PaymentTokenGovernorProxyContract.set_payment_token_governor(NewPaymentTokenGovernorContract, {'from': accounts[0]})

	assert PaymentTokenGovernorProxyContract.check_payment_token_acceptance(PaymentToken) == False
	assert PaymentTokenGovernorProxyContract.check_payment_token_acceptance(NewPaymentToken) == True
	assert PaymentTokenGovernorProxyContract.acceptedPaymentTokenCount() == 1
	assert PaymentTokenGovernorProxyContract.acceptedPaymentTokens(1) == NewPaymentToken
	assert PaymentTokenGovernorProxyContract.acceptedPaymentTokens(2) == ZERO_ADDRESS

	# Make payment in 2nd payment token

	payment2_1 = NewPaymentToken.approve(fdt_instance, 10000, {'from': accounts[0]})
	payment2_2 = fdt_instance.payToContract(5000, NewPaymentToken, {'from': accounts[0]})

	assert PaymentToken.balanceOf(fdt_instance) == 5000

	update_tx = fdt_instance.updateFundsTokenBalance({'from': accounts[0]})
	assert len(update_tx.events) == 1
	assert update_tx.events['FundsDistributed']['receiver'] == accounts[0]
	assert update_tx.events['FundsDistributed']['paymentToken'] == NewPaymentToken
	assert update_tx.events['FundsDistributed']['value'] == 5000

	account1_payment_token_balance = PaymentToken.balanceOf(accounts[0])
	account1_new_payment_token_balance = NewPaymentToken.balanceOf(accounts[0])
	account1_withdraw = fdt_instance.withdrawFunds({'from': accounts[0]})

	#assert len(account1_withdraw.events) ==1
	assert account1_withdraw.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw.events['FundsWithdrawn']['paymentToken'] == NewPaymentToken
	assert account1_withdraw.events['FundsWithdrawn']['value'] == 3000
	assert NewPaymentToken.balanceOf(fdt_instance) == 2000
	assert NewPaymentToken.balanceOf(accounts[0]) == account1_new_payment_token_balance + 3000

	assert PaymentToken.balanceOf(fdt_instance) == 5000
	assert PaymentToken.balanceOf(accounts[0]) == account1_payment_token_balance
