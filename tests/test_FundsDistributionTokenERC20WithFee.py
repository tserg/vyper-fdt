import pytest

from brownie import (
	accounts,
	ERC20,
	FeeGovernor,
	FeeGovernorProxy,
	FundsDistributionTokenERC20WithFee,
	FundsDistributionTokenERC20WithFeeFactory,
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

@pytest.fixture(scope="module")
def PaymentToken(ERC20, accounts):
	yield ERC20.deploy(PAYMENT_TOKEN_NAME, PAYMENT_TOKEN_SYMBOL, PAYMENT_TOKEN_DECIMALS, PAYMENT_TOKEN_SUPPLY, {'from': accounts[0]})

@pytest.fixture(scope="module")
def NewPaymentToken(ERC20, accounts):
	yield ERC20.deploy(NEW_PAYMENT_TOKEN_NAME, NEW_PAYMENT_TOKEN_SYMBOL, NEW_PAYMENT_TOKEN_DECIMALS, NEW_PAYMENT_TOKEN_SUPPLY, {'from': accounts[0]})

@pytest.fixture(scope="module")
def FeeGovernorContract(FeeGovernor, accounts):
	yield FeeGovernor.deploy(1e8, {'from': accounts[0]})

@pytest.fixture(scope="module")
def FeeGovernorProxyContract(FeeGovernorContract, FeeGovernorProxy, accounts):
	yield FeeGovernorProxy.deploy(FeeGovernorContract, {'from': accounts[0]})

@pytest.fixture(scope="module")
def FDTERC20Contract(FundsDistributionTokenERC20WithFee, accounts):
	yield FundsDistributionTokenERC20WithFee.deploy({'from': accounts[0]})

@pytest.fixture(scope="module")
def FDTERC20FactoryContract(PaymentToken, FDTERC20Contract, FundsDistributionTokenERC20WithFeeFactory, FeeGovernorProxyContract, accounts):
	yield FundsDistributionTokenERC20WithFeeFactory.deploy(FundsDistributionTokenERC20WithFee[0].address, accounts[0], PaymentToken.address, FeeGovernorProxyContract.address, {'from': accounts[0]})

@pytest.fixture(scope="module", autouse=True)
def test_deploy_fdt_from_factory(FDTERC20FactoryContract, PaymentToken, accounts):

	tx1 = FDTERC20FactoryContract.deploy_fdt_contract(TOKEN_NAME, TOKEN_SYMBOL, TOKEN_DECIMALS, TOKEN_SUPPLY, {'from': accounts[0]})

	global FDT_INSTANCE
	FDT_INSTANCE = tx1.new_contracts[0]

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
	pass

def test_initial_state(FDTERC20FactoryContract, accounts):

	fdt_instance = FundsDistributionTokenERC20WithFee.at(FDT_INSTANCE)

	assert fdt_instance.balanceOf(accounts[0]) == 100
	assert fdt_instance.balanceOf(accounts[1]) == 0

def test_same_IO(PaymentToken, accounts):

	"""
		Address with 100 tokens pays to contract, and withdraws
	"""
	fdt_instance = FundsDistributionTokenERC20WithFee.at(FDT_INSTANCE)
	tx1_1 = PaymentToken.approve(fdt_instance, 500e18, {'from': accounts[0]})
	tx1_2 = fdt_instance.payToContract(500e18, {'from': accounts[0]})

	assert PaymentToken.balanceOf(FundsDistributionTokenERC20WithFee[1]) == 500e18

	account_balance = PaymentToken.balanceOf(accounts[0])

	tx2 = fdt_instance.updateFundsTokenBalance({'from': accounts[0]})

	assert tx2.events['FundsDistributed']['receiver'] == accounts[0]
	assert fdt_instance.withdrawableFundsOf(accounts[0]) == 495e18

	tx3 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert tx3.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert PaymentToken.balanceOf(fdt_instance) == 5e18
	assert PaymentToken.balanceOf(accounts[0]) == account_balance + 495e18

	tx4 = fdt_instance.withdrawAdminFee({'from': accounts[0]})
	assert PaymentToken.balanceOf(fdt_instance) == 0
	assert tx4.events['AdminFeeWithdrawn']['beneficiary'] == accounts[0]
	assert tx4.events['AdminFeeWithdrawn']['value'] == 5e18


def test_different_IO_single_deposit(PaymentToken, accounts):

	"""
		Non-token holding address pays to contract, address with 100 tokens withdraws
	"""
	fdt_instance = FundsDistributionTokenERC20WithFee.at(FDT_INSTANCE)
	tx0 = PaymentToken.transfer(accounts[1], 500e18, {'from': accounts[0]})
	tx1_1 = PaymentToken.approve(fdt_instance, 500e18, {'from': accounts[1]})
	tx1_2 = fdt_instance.payToContract(500e18, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 500e18

	account_balance = PaymentToken.balanceOf(accounts[0])

	tx2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert tx2.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert PaymentToken.balanceOf(fdt_instance) == 5e18
	assert PaymentToken.balanceOf(accounts[0]) == account_balance + 495e18

	account_balance = PaymentToken.balanceOf(accounts[0])

	tx3 = fdt_instance.withdrawAdminFee({'from': accounts[0]})
	assert PaymentToken.balanceOf(fdt_instance) == 0
	assert tx3.events['AdminFeeWithdrawn']['beneficiary'] == accounts[0]
	assert tx3.events['AdminFeeWithdrawn']['value'] == 5e18
	assert PaymentToken.balanceOf(accounts[0]) == account_balance + 5e18

def test_two_token_holders_single_deposit(PaymentToken, accounts):

	"""
		Two address with 50 tokens each, withdraws
	"""
	fdt_instance = FundsDistributionTokenERC20WithFee.at(FDT_INSTANCE)
	tx1 = fdt_instance.transfer(accounts[1], 50, {'from': accounts[0]})

	tx2_1 = PaymentToken.transfer(accounts[1], 500e18, {'from': accounts[0]})
	tx2_2 = PaymentToken.approve(fdt_instance, 500e18, {'from': accounts[1]})
	tx2_3 = fdt_instance.payToContract(500e18, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 500e18

	account_balance = PaymentToken.balanceOf(accounts[0])

	tx3 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert tx3.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx3.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert PaymentToken.balanceOf(fdt_instance) == 252.5e18
	assert PaymentToken.balanceOf(accounts[0]) == account_balance + 247.5e18

	account_balance = PaymentToken.balanceOf(accounts[1])

	tx4 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert tx4.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert PaymentToken.balanceOf(fdt_instance) == 5e18
	assert PaymentToken.balanceOf(accounts[1]) == account_balance + 247.5e18

	account_balance = PaymentToken.balanceOf(accounts[0])

	tx5 = fdt_instance.withdrawAdminFee({'from': accounts[0]})
	assert PaymentToken.balanceOf(fdt_instance) == 0
	assert tx5.events['AdminFeeWithdrawn']['beneficiary'] == accounts[0]
	assert tx5.events['AdminFeeWithdrawn']['value'] == 5e18
	assert PaymentToken.balanceOf(accounts[0]) == account_balance + 5e18

def test_three_token_holders_single_deposit(PaymentToken, accounts):
	"""
		Single payer, three addresses withdraws
	"""
	fdt_instance = FundsDistributionTokenERC20WithFee.at(FDT_INSTANCE)
	tx1_1 = fdt_instance.transfer(accounts[1], 25, {'from': accounts[0]})
	tx1_2 = fdt_instance.transfer(accounts[2], 35, {'from': accounts[0]})

	tx2_1 = PaymentToken.transfer(accounts[1], 500e18, {'from': accounts[0]})
	tx2_2 = PaymentToken.approve(fdt_instance, 500e18, {'from': accounts[1]})
	tx2_3 = fdt_instance.payToContract(500e18, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 500e18

	account1_balance = PaymentToken.balanceOf(accounts[0])

	tx3 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert tx3.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx3.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert PaymentToken.balanceOf(fdt_instance) == 302e18
	assert PaymentToken.balanceOf(accounts[0]) == account1_balance + 198e18

	account2_balance = PaymentToken.balanceOf(accounts[1])

	tx4 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert tx4.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert PaymentToken.balanceOf(fdt_instance) == 178.25e18
	assert PaymentToken.balanceOf(accounts[1]) == account2_balance + 123.75e18

	account3_balance = PaymentToken.balanceOf(accounts[2])

	tx5 = fdt_instance.withdrawFunds({'from': accounts[2]})

	assert tx5.events['FundsWithdrawn']['receiver'] == accounts[2]
	assert PaymentToken.balanceOf(fdt_instance) == 5e18
	assert PaymentToken.balanceOf(accounts[2]) == account3_balance + 173.25e18

def test_different_IO_single_deposit_with_token_transfer(PaymentToken, accounts):

	"""
		Account holding 100 tokens pays to contract, transfers all tokens to another address.
		Both withdraws.
	"""
	fdt_instance = FundsDistributionTokenERC20WithFee.at(FDT_INSTANCE)
	tx1_2 = PaymentToken.approve(fdt_instance, 500e18, {'from': accounts[0]})
	tx1_3 = fdt_instance.payToContract(500e18, {'from': accounts[0]})

	assert PaymentToken.balanceOf(fdt_instance) == 500e18

	update_tx = fdt_instance.updateFundsTokenBalance({'from': accounts[0]})
	assert update_tx.events['FundsDistributed']['receiver'] == accounts[0]

	FDT_transfer = fdt_instance.transfer(accounts[1], 100, {'from': accounts[0]})

	assert fdt_instance.balanceOf(accounts[0]) == 0

	account1_balance = PaymentToken.balanceOf(accounts[0])
	account2_balance = PaymentToken.balanceOf(accounts[1])

	account1_withdraw = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert account1_withdraw.events['FundsWithdrawn']['receiver'] == accounts[0]
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
	fdt_instance = FundsDistributionTokenERC20WithFee.at(FDT_INSTANCE)
	FDT_transfer = fdt_instance.transfer(accounts[1], 40, {'from': accounts[0]})

	assert FDT_transfer.events['Transfer']['sender'] == accounts[0]
	assert FDT_transfer.events['Transfer']['receiver'] == accounts[1]
	assert FDT_transfer.events['Transfer']['value'] == 40

	payment1_1 = PaymentToken.transfer(accounts[1], 2000e18, {'from': accounts[0]})
	payment1_2 = PaymentToken.approve(fdt_instance, 2000e18, {'from': accounts[1]})
	payment1_3 = fdt_instance.payToContract(1000e18, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 1000e18

	account1_balance1 = PaymentToken.balanceOf(accounts[0])

	account1_withdrawa1 = fdt_instance.withdrawFunds({'from': accounts[0]})
	assert account1_withdrawa1.events['FundsDistributed']['receiver'] == accounts[0]
	assert account1_withdrawa1.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdrawa1.events['FundsWithdrawn']['value'] == 594e18
	assert PaymentToken.balanceOf(fdt_instance) == 406e18
	assert PaymentToken.balanceOf(accounts[0]) == account1_balance1 + 594e18
	assert fdt_instance.adminFeeTokenBalance() == 10e18

	payment2_1 = PaymentToken.approve(fdt_instance, 1000e18, {'from': accounts[1]})
	payment2_1 = fdt_instance.payToContract(1000e18, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 1406e18


	account2_balance = PaymentToken.balanceOf(accounts[1])

	update_tx = fdt_instance.updateFundsTokenBalance({'from': accounts[0]})
	assert update_tx.events['FundsDistributed']['receiver'] == accounts[0]
	assert update_tx.events['FundsDistributed']['value'] == 1000e18
	assert fdt_instance.adminFeeTokenBalance() == 20e18

	account2_withdrawa1 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert account2_withdrawa1.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert account2_withdrawa1.events['FundsWithdrawn']['value'] == 792e18
	assert PaymentToken.balanceOf(fdt_instance) == 614e18
	assert PaymentToken.balanceOf(accounts[1]) == account2_balance + 792e18


	account1_balance2 = PaymentToken.balanceOf(accounts[0])

	account1_withdraw2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert account1_withdraw2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw2.events['FundsWithdrawn']['value'] == 594e18
	assert PaymentToken.balanceOf(fdt_instance) == 20e18
	assert PaymentToken.balanceOf(accounts[0]) == account1_balance2 + 594e18

	account_balance = PaymentToken.balanceOf(accounts[0])

	withdraw_admin_fee = fdt_instance.withdrawAdminFee({'from': accounts[0]})
	assert PaymentToken.balanceOf(fdt_instance) == 0
	assert withdraw_admin_fee.events['AdminFeeWithdrawn']['beneficiary'] == accounts[0]
	assert withdraw_admin_fee.events['AdminFeeWithdrawn']['value'] == 20e18
	assert PaymentToken.balanceOf(accounts[0]) == account_balance + 20e18

def test_multiple_deposit_lower_value_with_intervening_transfer_two_withdrawals(PaymentToken, accounts):
	"""
		Two addresses holding tokens.
		One deposit is made.
		One address withdraws.
		Another deposit is made that results in contract balance < first deposit.
		Both addresses withdraw.
	"""
	fdt_instance = FundsDistributionTokenERC20WithFee.at(FDT_INSTANCE)
	FDT_transfer = fdt_instance.transfer(accounts[1], 40, {'from': accounts[0]})

	assert FDT_transfer.events['Transfer']['sender'] == accounts[0]
	assert FDT_transfer.events['Transfer']['receiver'] == accounts[1]
	assert FDT_transfer.events['Transfer']['value'] == 40

	payment1_1 = PaymentToken.transfer(accounts[1], 10000e18, {'from': accounts[0]})
	payment1_2 = PaymentToken.approve(fdt_instance, 10000e18, {'from': accounts[1]})
	payment1_3 = fdt_instance.payToContract(5000e18, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 5000e18

	account1_balance1 = PaymentToken.balanceOf(accounts[0])

	account1_withdraw1 = fdt_instance.withdrawFunds({'from': accounts[0]})
	assert account1_withdraw1.events['FundsDistributed']['receiver'] == accounts[0]
	assert account1_withdraw1.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw1.events['FundsWithdrawn']['value'] == 2970e18
	assert PaymentToken.balanceOf(fdt_instance) == 2030e18
	assert PaymentToken.balanceOf(accounts[0]) == account1_balance1 + 2970e18


	payment1 = fdt_instance.payToContract(1000e18, {'from': accounts[1]})

	assert PaymentToken.balanceOf(fdt_instance) == 3030e18

	account2_balance = PaymentToken.balanceOf(accounts[1])

	update_tx = fdt_instance.updateFundsTokenBalance({'from': accounts[0]})
	assert update_tx.events['FundsDistributed']['receiver'] == accounts[0]
	assert update_tx.events['FundsDistributed']['value'] == 1000e18

	account2_withdraw1 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert account2_withdraw1.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert account2_withdraw1.events['FundsWithdrawn']['value'] == 2376e18
	assert PaymentToken.balanceOf(fdt_instance) == 654e18
	assert PaymentToken.balanceOf(accounts[1]) == account2_balance + 2376e18


	account1_balance2 = PaymentToken.balanceOf(accounts[0])

	account1_withdraw2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert account1_withdraw2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw2.events['FundsWithdrawn']['value'] == 594e18
	assert PaymentToken.balanceOf(fdt_instance) == 60e18
	assert PaymentToken.balanceOf(accounts[0]) == account1_balance2 + 594e18

	account_balance = PaymentToken.balanceOf(accounts[0])

	withdraw_admin_fee = fdt_instance.withdrawAdminFee({'from': accounts[0]})
	assert PaymentToken.balanceOf(fdt_instance) == 0
	assert withdraw_admin_fee.events['AdminFeeWithdrawn']['beneficiary'] == accounts[0]
	assert withdraw_admin_fee.events['AdminFeeWithdrawn']['value'] == 60e18
	assert PaymentToken.balanceOf(accounts[0]) == account_balance + 60e18
