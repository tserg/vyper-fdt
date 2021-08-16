import pytest

from brownie import (
	accounts,
	FundsDistributionToken,
	FundsDistributionTokenFactory,
)

TOKEN_NAME = "MetaCoin"
TOKEN_SYMBOL = "MCC"
TOKEN_DECIMALS = 0
TOKEN_SUPPLY = 100



@pytest.fixture(scope="module", autouse=True)
def FDTContract(FundsDistributionToken, accounts):
	yield FundsDistributionToken.deploy({'from': accounts[0]})

@pytest.fixture(scope="module", autouse=True)
def FDTFactoryContract(FDTContract, FundsDistributionTokenFactory, accounts):
	yield FundsDistributionTokenFactory.deploy(FundsDistributionToken[0].address, accounts[0], {'from': accounts[0]})

@pytest.fixture(scope="module", autouse=True)
def fdt_instance(FDTFactoryContract, FundsDistributionToken, accounts):

	tx1 = FDTFactoryContract.deploy_fdt_contract(TOKEN_NAME, TOKEN_SYMBOL, TOKEN_DECIMALS, TOKEN_SUPPLY, {'from': accounts[0]})

	yield FundsDistributionToken.at(tx1.new_contracts[0])

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
	pass

def test_initial_state(fdt_instance, accounts):

	assert fdt_instance.balanceOf(accounts[0]) == 100
	assert fdt_instance.balanceOf(accounts[1]) == 0

def test_same_IO(fdt_instance, accounts):

	"""
		Address with 100 tokens pays to contract, and withdraws
	"""
	tx1 = accounts[0].transfer(fdt_instance, '1 ether')

	assert fdt_instance.balance() == 1e18

	account_balance = accounts[0].balance()

	tx2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert len(tx2.events) == 2
	assert tx2.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert fdt_instance.balance() == 0
	assert accounts[0].balance() == account_balance + 1e18


def test_different_IO_single_deposit(fdt_instance, accounts):

	"""
		Non-token holding address pays to contract, address with 100 tokens withdraws
	"""
	tx1 = accounts[1].transfer(fdt_instance, '1 ether')

	assert fdt_instance.balance() == 1e18

	account_balance = accounts[0].balance()

	tx2 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert len(tx2.events) == 2
	assert tx2.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert fdt_instance.balance() == 0
	assert accounts[0].balance() == account_balance + 1e18


def test_two_token_holders_single_deposit(fdt_instance, accounts):

	"""
		Two address with 50 tokens each, withdraws
	"""
	tx1 = fdt_instance.transfer(accounts[1], 50, {'from': accounts[0]})

	assert len(tx1.events) == 1

	tx2 = accounts[1].transfer(fdt_instance, '1 ether')

	assert fdt_instance.balance() == 1e18

	account_balance = accounts[0].balance()

	tx3 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert len(tx3.events) == 2
	assert tx3.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx3.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert fdt_instance.balance() == 5e17
	assert accounts[0].balance() == account_balance + 5e17

	account_balance = accounts[1].balance()

	tx4 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert len(tx4.events) == 1
	assert tx4.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert fdt_instance.balance() == 0
	assert accounts[1].balance() == account_balance + 5e17


def test_three_token_holders_single_deposit(fdt_instance, accounts):
	"""
		Single payer, three addresses withdraws
	"""
	tx1_1 = fdt_instance.transfer(accounts[1], 25, {'from': accounts[0]})
	tx1_2 = fdt_instance.transfer(accounts[2], 35, {'from': accounts[0]})
	tx2 = accounts[1].transfer(fdt_instance, '1 ether', )

	assert fdt_instance.balance() == 1e18

	account1_balance = accounts[0].balance()

	tx3 = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert len(tx3.events) == 2
	assert tx3.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx3.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert fdt_instance.balance() == 0.6e18
	assert accounts[0].balance() == account1_balance + 0.4e18

	account2_balance = accounts[1].balance()

	tx4 = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert len(tx4.events) == 1
	assert tx4.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert fdt_instance.balance() == 0.35e18
	assert accounts[1].balance() == account2_balance + 0.25e18

	account3_balance = accounts[2].balance()

	tx5 = fdt_instance.withdrawFunds({'from': accounts[2]})

	assert len(tx5.events) == 1
	assert tx5.events['FundsWithdrawn']['receiver'] == accounts[2]
	assert fdt_instance.balance() == 0
	assert accounts[2].balance() == account3_balance + 0.35e18


def test_different_IO_single_deposit_with_token_transfer(fdt_instance, accounts):

	"""
		Token holding 100 tokens pays to contract, transfers all tokens to another address.
		Both withdraws.
	"""
	tx1 = accounts[1].transfer(fdt_instance, '1 ether')

	assert fdt_instance.balance() == 1e18

	FDT_transfer = fdt_instance.transfer(accounts[1], 100, {'from': accounts[0]})

	assert len(FDT_transfer.events) == 1

	account1_balance = accounts[0].balance()
	account2_balance = accounts[1].balance()

	account1_withdraw = fdt_instance.withdrawFunds({'from': accounts[0]})

	assert len(account1_withdraw.events) == 2
	assert account1_withdraw.events['FundsDistributed']['receiver'] == accounts[0]
	assert account1_withdraw.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw.events['FundsWithdrawn']['value'] == 0
	assert fdt_instance.balance() == 1e18
	assert accounts[0].balance () == account1_balance

	account2_withdraw = fdt_instance.withdrawFunds({'from': accounts[1]})

	assert len(account2_withdraw.events) == 1
	assert fdt_instance.balance() == 0
	assert accounts[1].balance() == account2_balance + 1e18

def test_multiple_deposit_with_intervening_transfer_two_withdrawals(fdt_instance, accounts):
	"""
		Two addresses holding tokens.
		One deposit is made.
		One address withdraws.
		Another deposit is made.
		Both addresses withdraw.
	"""
	FDT_transfer = fdt_instance.transfer(accounts[1], 40, {'from': accounts[0]})

	assert len(FDT_transfer.events) == 1

	payment1 = accounts[1].transfer(fdt_instance, '1 ether')

	assert fdt_instance.balance() == 1e18

	account1_balance1 = accounts[0].balance()

	account1_withdraw1 = fdt_instance.withdrawFunds({'from': accounts[0]})
	assert len(account1_withdraw1.events) == 2
	assert account1_withdraw1.events['FundsDistributed']['receiver'] == accounts[0]
	assert account1_withdraw1.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw1.events['FundsWithdrawn']['value'] == 0.6e18
	assert fdt_instance.balance() == 0.4e18
	assert accounts[0].balance () == account1_balance1 + 0.6e18

	payment2 = accounts[1].transfer(fdt_instance, '2 ether')

	assert fdt_instance.balance() == 2.4e18

	account2_balance = accounts[1].balance()

	account2_withdraw1 = fdt_instance.withdrawFunds({'from': accounts[1]})
	assert len(account2_withdraw1.events) == 2
	assert account2_withdraw1.events['FundsDistributed']['receiver'] == accounts[1]
	assert account2_withdraw1.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert account2_withdraw1.events['FundsWithdrawn']['value'] == 1.2e18
	assert fdt_instance.balance() == 1.2e18
	assert accounts[1].balance () == account2_balance + 1.2e18

	account1_balance2 = accounts[0].balance()

	account1_withdraw2 = fdt_instance.withdrawFunds({'from': accounts[0]})
	assert len(account1_withdraw2.events) == 1
	assert account1_withdraw2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw2.events['FundsWithdrawn']['value'] == 1.2e18
	assert fdt_instance.balance() == 0
	assert accounts[0].balance () == account1_balance2 + 1.2e18

def test_multiple_deposit_lower_value_with_intervening_transfer_two_withdrawals(fdt_instance, accounts):
	"""
		Two addresses holding tokens.
		One deposit is made.
		One address withdraws.
		Another deposit is made that results in contract balance < first deposit.
		Both addresses withdraw.
	"""
	FDT_transfer = fdt_instance.transfer(accounts[1], 40, {'from': accounts[0]})

	assert len(FDT_transfer.events) == 1

	payment1 = accounts[1].transfer(fdt_instance, '5 ether')

	assert fdt_instance.balance() == 5e18

	account1_balance1 = accounts[0].balance()

	account1_withdraw1 = fdt_instance.withdrawFunds({'from': accounts[0]})
	assert len(account1_withdraw1.events) == 2
	assert account1_withdraw1.events['FundsDistributed']['receiver'] == accounts[0]
	assert account1_withdraw1.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw1.events['FundsWithdrawn']['value'] == 3e18
	assert fdt_instance.balance() == 2e18
	assert accounts[0].balance () == account1_balance1 + 3e18

	payment1 = accounts[1].transfer(fdt_instance, '1 ether')

	assert fdt_instance.balance() == 3e18

	account2_balance = accounts[1].balance()

	account2_withdraw1 = fdt_instance.withdrawFunds({'from': accounts[1]})
	assert len(account2_withdraw1.events) == 2
	assert account2_withdraw1.events['FundsDistributed']['receiver'] == accounts[1]
	assert account2_withdraw1.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert account2_withdraw1.events['FundsWithdrawn']['value'] == 2.4e18
	assert fdt_instance.balance() == 0.6e18
	assert accounts[1].balance () == account2_balance + 2.4e18

	account1_balance2 = accounts[0].balance()

	account1_withdraw2 = fdt_instance.withdrawFunds({'from': accounts[0]})
	assert len(account1_withdraw2.events) == 1
	assert account1_withdraw2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert account1_withdraw2.events['FundsWithdrawn']['value'] == 0.6e18
	assert fdt_instance.balance() == 0
	assert accounts[0].balance () == account1_balance2 + 0.6e18
