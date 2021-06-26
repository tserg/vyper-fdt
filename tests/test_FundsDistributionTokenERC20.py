import pytest

from brownie import (
	accounts,
	ERC20,
	FundsDistributionTokenERC20,
	FundsDistributionTokenERC20Factory,
)

PAYMENT_TOKEN_NAME = "Dai"
PAYMENT_TOKEN_SYMBOL = "DAI"
PAYMENT_TOKEN_DECIMALS = 18
PAYMENT_TOKEN_SUPPLY = 1000

TOKEN_NAME = "MetaCoin"
TOKEN_SYMBOL = "MCC"
TOKEN_DECIMALS = 0
TOKEN_SUPPLY = 100

@pytest.fixture(scope="module")
def ERC20(ERC20, accounts):
	yield ERC20.deploy(PAYMENT_TOKEN_NAME, PAYMENT_TOKEN_SYMBOL, PAYMENT_TOKEN_DECIMALS, PAYMENT_TOKEN_SUPPLY, {'from': accounts[0]})

@pytest.fixture(scope="module")
def FDTERC20Contract(FundsDistributionTokenERC20, accounts):
	yield FundsDistributionTokenERC20.deploy({'from': accounts[0]})

@pytest.fixture(scope="module")
def FDTERC20FactoryContract(ERC20, FDTERC20Contract, FundsDistributionTokenERC20Factory, accounts):
	yield FundsDistributionTokenERC20Factory.deploy(FundsDistributionTokenERC20[0].address, accounts[0], ERC20.address, {'from': accounts[0]})

@pytest.fixture(scope="module", autouse=True)
def test_deploy_fdt_from_factory(FDTERC20FactoryContract, ERC20, accounts):

	tx1 = FDTERC20FactoryContract.deploy_fdt_contract(TOKEN_NAME, TOKEN_SYMBOL, TOKEN_DECIMALS, TOKEN_SUPPLY, {'from': accounts[0]})

	global FDT_INSTANCE
	FDT_INSTANCE = tx1.new_contracts[0]

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
	pass

def test_initial_state(FDTERC20FactoryContract, accounts):

	fdt_instance = FundsDistributionTokenERC20.at(FDT_INSTANCE)

	assert FundsDistributionTokenERC20[1].balanceOf(accounts[0]) == 100
	assert FundsDistributionTokenERC20[1].balanceOf(accounts[1]) == 0

def test_same_IO(ERC20, accounts):

	"""
		Address with 100 tokens pays to contract, and withdraws
	"""
	fdt_instance = FundsDistributionTokenERC20.at(FDT_INSTANCE)
	tx1_1 = ERC20.approve(FundsDistributionTokenERC20[1], 500, {'from': accounts[0]})
	tx1_2 = FundsDistributionTokenERC20[1].payToContract(500, {'from': accounts[0]})

	assert ERC20.balanceOf(FundsDistributionTokenERC20[1]) == 500

	account_balance = ERC20.balanceOf(accounts[0])

	tx2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert tx2.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert ERC20.balanceOf(FundsDistributionTokenERC20[1]) == 0
	assert ERC20.balanceOf(accounts[0]) == account_balance + 500

def test_different_IO_single_deposit(ERC20, accounts):

	"""
		Non-token holding address pays to contract, address with 100 tokens withdraws
	"""
	fdt_instance = FundsDistributionTokenERC20.at(FDT_INSTANCE)
	tx0 = ERC20.transfer(accounts[1], 500, {'from': accounts[0]})
	tx1_1 = ERC20.approve(FundsDistributionTokenERC20[1], 500, {'from': accounts[1]})
	tx1_2 = FundsDistributionTokenERC20[1].payToContract(500, {'from': accounts[1]})

	assert ERC20.balanceOf(FundsDistributionTokenERC20[1]) == 500

	account_balance = ERC20.balanceOf(accounts[0])

	tx2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert tx2.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert ERC20.balanceOf(fdt_instance) == 0
	assert ERC20.balanceOf(accounts[0]) == account_balance + 500

def test_two_token_holders_single_deposit(ERC20, accounts):

	"""
		Two address with 50 tokens each, withdraws
	"""
	fdt_instance = FundsDistributionTokenERC20.at(FDT_INSTANCE)
	tx1 = fdt_instance.transfer(accounts[1], 50, {'from': accounts[0]})

	tx2_1 = ERC20.transfer(accounts[1], 500, {'from': accounts[0]})
	tx2_2 = ERC20.approve(FundsDistributionTokenERC20[1], 500, {'from': accounts[1]})
	tx2_3 = FundsDistributionTokenERC20[1].payToContract(500, {'from': accounts[1]})

	assert ERC20.balanceOf(FundsDistributionTokenERC20[1]) == 500

	account_balance = ERC20.balanceOf(accounts[0])

	tx3 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert tx3.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx3.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert ERC20.balanceOf(fdt_instance) == 250
	assert ERC20.balanceOf(accounts[0]) == account_balance + 250

	account_balance = ERC20.balanceOf(accounts[1])

	tx4 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert tx4.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert ERC20.balanceOf(fdt_instance) == 0
	assert ERC20.balanceOf(accounts[1]) == account_balance + 250

def test_three_token_holders_single_deposit(ERC20, accounts):
	"""
		Single payer, three addresses withdraws
	"""
	fdt_instance = FundsDistributionTokenERC20.at(FDT_INSTANCE)
	tx1_1 = fdt_instance.transfer(accounts[1], 25, {'from': accounts[0]})
	tx1_2 = fdt_instance.transfer(accounts[2], 35, {'from': accounts[0]})

	tx2_1 = ERC20.transfer(accounts[1], 500, {'from': accounts[0]})
	tx2_2 = ERC20.approve(FundsDistributionTokenERC20[1], 500, {'from': accounts[1]})
	tx2_3 = FundsDistributionTokenERC20[1].payToContract(500, {'from': accounts[1]})

	assert ERC20.balanceOf(FundsDistributionTokenERC20[1]) == 500

	account1_balance = ERC20.balanceOf(accounts[0])

	tx3 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert tx3.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx3.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert ERC20.balanceOf(fdt_instance) == 300
	assert ERC20.balanceOf(accounts[0]) == account1_balance + 200

	account2_balance = ERC20.balanceOf(accounts[1])

	tx4 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert tx4.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert ERC20.balanceOf(fdt_instance) == 175
	assert ERC20.balanceOf(accounts[1]) == account2_balance + 125

	account3_balance = ERC20.balanceOf(accounts[2])

	tx5 = fdt_instance.withdrawFunds({'from': accounts[2]})

	assert tx5.events['FundsWithdrawn']['receiver'] == accounts[2]
	assert ERC20.balanceOf(fdt_instance) == 0
	assert ERC20.balanceOf(accounts[2]) == account3_balance + 175

def test_different_IO_single_deposit_with_token_transfer(ERC20, accounts):

	"""
		Account holding 100 tokens pays to contract, transfers all tokens to another address.
		Both withdraws.
	"""
	fdt_instance = FundsDistributionTokenERC20.at(FDT_INSTANCE)
	tx1_2 = ERC20.approve(FundsDistributionTokenERC20[1], 500, {'from': accounts[0]})
	tx1_3 = FundsDistributionTokenERC20[1].payToContract(500, {'from': accounts[0]})

	assert ERC20.balanceOf(FundsDistributionTokenERC20[1]) == 500

	update_tx = fdt_instance.updateFundsTokenBalance({'from': accounts[0]})
	assert update_tx.events['FundsDistributed']['receiver'] == accounts[0]

	FDT_transfer = fdt_instance.transfer(accounts[1], 100, {'from': accounts[0]})

	assert fdt_instance.balanceOf(accounts[0]) == 0

	account1_balance = ERC20.balanceOf(accounts[0])
	account2_balance = ERC20.balanceOf(accounts[1])

	account1_withdraw = fdt_instance.withdrawFunds({'from': accounts[0]})


	assert account1_withdraw.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw.events['FundsWithdrawn']['value'] == 0
	assert ERC20.balanceOf(fdt_instance) == 500
	assert ERC20.balanceOf(accounts[0]) == account1_balance

	account2_withdraw = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert ERC20.balanceOf(fdt_instance) == 0
	assert ERC20.balanceOf(accounts[1]) == account2_balance + 500

def test_multiple_deposit_with_intervening_transfer_two_withdrawals(ERC20, accounts):
	"""
		Two addresses holding tokens.
		One deposit is made.
		One address withdraws.
		Another deposit is made.
		Both addresses withdraw.
	"""
	fdt_instance = FundsDistributionTokenERC20.at(FDT_INSTANCE)
	FDT_transfer = fdt_instance.transfer(accounts[1], 40, {'from': accounts[0]})

	assert FDT_transfer.events['Transfer']['sender'] == accounts[0]
	assert FDT_transfer.events['Transfer']['receiver'] == accounts[1]
	assert FDT_transfer.events['Transfer']['value'] == 40

	payment1_1 = ERC20.transfer(accounts[1], 2000, {'from': accounts[0]})
	payment1_2 = ERC20.approve(FundsDistributionTokenERC20[1], 2000, {'from': accounts[1]})
	payment1_3 = FundsDistributionTokenERC20[1].payToContract(1000, {'from': accounts[1]})

	assert ERC20.balanceOf(fdt_instance) == 1000

	account1_balance1 = ERC20.balanceOf(accounts[0])

	account1_withdrawa1 = fdt_instance.withdrawFunds({'from': accounts[0]})
	assert account1_withdrawa1.events['FundsDistributed']['receiver'] == accounts[0]
	assert account1_withdrawa1.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdrawa1.events['FundsWithdrawn']['value'] == 600
	assert ERC20.balanceOf(fdt_instance) == 400
	assert ERC20.balanceOf(accounts[0]) == account1_balance1 + 600

	payment2_1 = ERC20.approve(FundsDistributionTokenERC20[1], 1000, {'from': accounts[1]})
	payment2_1 = FundsDistributionTokenERC20[1].payToContract(1000, {'from': accounts[1]})

	assert ERC20.balanceOf(fdt_instance) == 1400

	account2_balance = ERC20.balanceOf(accounts[1])

	update_tx = fdt_instance.updateFundsTokenBalance({'from': accounts[0]})
	assert update_tx.events['FundsDistributed']['receiver'] == accounts[0]
	assert update_tx.events['FundsDistributed']['value'] == 1000


	account2_withdrawa1 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert account2_withdrawa1.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert account2_withdrawa1.events['FundsWithdrawn']['value'] == 800
	assert ERC20.balanceOf(fdt_instance) == 600
	assert ERC20.balanceOf(accounts[1]) == account2_balance + 800


	account1_balance2 = ERC20.balanceOf(accounts[0])

	account1_withdraw2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert account1_withdraw2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw2.events['FundsWithdrawn']['value'] == 600
	assert ERC20.balanceOf(fdt_instance) == 0
	assert ERC20.balanceOf(accounts[0]) == account1_balance2 + 600

def test_multiple_deposit_lower_value_with_intervening_transfer_two_withdrawals(ERC20, accounts):
	"""
		Two addresses holding tokens.
		One deposit is made.
		One address withdraws.
		Another deposit is made that results in contract balance < first deposit.
		Both addresses withdraw.
	"""
	fdt_instance = FundsDistributionTokenERC20.at(FDT_INSTANCE)
	FDT_transfer = fdt_instance.transfer(accounts[1], 40, {'from': accounts[0]})

	assert FDT_transfer.events['Transfer']['sender'] == accounts[0]
	assert FDT_transfer.events['Transfer']['receiver'] == accounts[1]
	assert FDT_transfer.events['Transfer']['value'] == 40

	payment1_1 = ERC20.transfer(accounts[1], 10000, {'from': accounts[0]})
	payment1_2 = ERC20.approve(FundsDistributionTokenERC20[1], 10000, {'from': accounts[1]})
	payment1_3 = FundsDistributionTokenERC20[1].payToContract(5000, {'from': accounts[1]})

	assert ERC20.balanceOf(fdt_instance) == 5000

	account1_balance1 = ERC20.balanceOf(accounts[0])

	account1_withdraw1 = fdt_instance.withdrawFunds({'from': accounts[0]})
	assert account1_withdraw1.events['FundsDistributed']['receiver'] == accounts[0]
	assert account1_withdraw1.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw1.events['FundsWithdrawn']['value'] == 3000
	assert ERC20.balanceOf(fdt_instance) == 2000
	assert ERC20.balanceOf(accounts[0]) == account1_balance1 + 3000


	payment1 = FundsDistributionTokenERC20[1].payToContract(1000, {'from': accounts[1]})

	assert ERC20.balanceOf(fdt_instance) == 3000

	account2_balance = ERC20.balanceOf(accounts[1])

	update_tx = fdt_instance.updateFundsTokenBalance({'from': accounts[0]})
	assert update_tx.events['FundsDistributed']['receiver'] == accounts[0]
	assert update_tx.events['FundsDistributed']['value'] == 1000

	account2_withdraw1 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert account2_withdraw1.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert account2_withdraw1.events['FundsWithdrawn']['value'] == 2400
	assert ERC20.balanceOf(fdt_instance) == 600
	assert ERC20.balanceOf(accounts[1]) == account2_balance + 2400


	account1_balance2 = ERC20.balanceOf(accounts[0])

	account1_withdraw2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert account1_withdraw2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw2.events['FundsWithdrawn']['value'] == 600
	assert ERC20.balanceOf(fdt_instance) == 0
	assert ERC20.balanceOf(accounts[0]) == account1_balance2 + 600
