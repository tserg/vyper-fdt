import pytest

from brownie import accounts

TOKEN_NAME = "MetaCoin"
TOKEN_SYMBOL = "MCC"
TOKEN_DECIMALS = 0
TOKEN_SUPPLY = 100

@pytest.fixture
def FDT_contract(FundsDistributionToken, accounts):

	yield FundsDistributionToken.deploy(TOKEN_NAME, TOKEN_SYMBOL, TOKEN_DECIMALS, TOKEN_SUPPLY, {'from': accounts[0]})

def test_initial_state(FDT_contract, accounts):

	assert FDT_contract.balanceOf(accounts[0]) == 100
	assert FDT_contract.balanceOf(accounts[1]) == 0

def test_same_IO(FDT_contract, accounts):

	"""
		Address with 100 tokens pays to contract, and withdraws
	"""

	tx1 = FDT_contract.payToContract({'from': accounts[0], 'amount': 1e18})

	assert FDT_contract.balance() == 1e18

	account_balance = accounts[0].balance()

	tx2 = FDT_contract.withdrawFunds({'from': accounts[0]})

	assert len(tx2.events) == 2
	assert tx2.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert FDT_contract.balance() == 0
	assert accounts[0].balance() == account_balance + 1e18

def test_different_IO_single_deposit(FDT_contract, accounts):

	"""
		Non-token holding address pays to contract, address with 100 tokens withdraws
	"""
	tx1 = FDT_contract.payToContract({'from': accounts[1], 'amount': 1e18})

	assert FDT_contract.balance() == 1e18

	account_balance = accounts[0].balance()

	tx2 = FDT_contract.withdrawFunds({'from': accounts[0]})

	assert len(tx2.events) == 2
	assert tx2.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx2.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert FDT_contract.balance() == 0
	assert accounts[0].balance() == account_balance + 1e18

def test_two_token_holders_single_deposit(FDT_contract, accounts):

	"""
		Two address with 50 tokens each, withdraws
	"""

	tx1 = FDT_contract.transfer(accounts[1], 50, {'from': accounts[0]})

	assert len(tx1.events) == 1

	tx2 = FDT_contract.payToContract({'from': accounts[1], 'amount': 1e18})

	assert FDT_contract.balance() == 1e18

	account_balance = accounts[0].balance()

	tx3 = FDT_contract.withdrawFunds({'from': accounts[0]})

	assert len(tx3.events) == 2
	assert tx3.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx3.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert FDT_contract.balance() == 5e17
	assert accounts[0].balance() == account_balance + 5e17

	account_balance = accounts[1].balance()

	tx4 = FDT_contract.withdrawFunds({'from': accounts[1]})

	assert len(tx4.events) == 1
	assert tx4.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert FDT_contract.balance() == 0
	assert accounts[1].balance() == account_balance + 5e17

def test_three_token_holders_single_deposit(FDT_contract, accounts):
	"""
		Single payer, three addresses withdraws
	"""

	tx1_1 = FDT_contract.transfer(accounts[1], 25, {'from': accounts[0]})

	assert len(tx1_1.events) == 1

	tx1_2 = FDT_contract.transfer(accounts[2], 35, {'from': accounts[0]})

	assert len(tx1_2.events) == 1

	tx2 = FDT_contract.payToContract({'from': accounts[1], 'amount': 1e18})

	assert FDT_contract.balance() == 1e18

	account1_balance = accounts[0].balance()

	tx3 = FDT_contract.withdrawFunds({'from': accounts[0]})

	assert len(tx3.events) == 2
	assert tx3.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx3.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert FDT_contract.balance() == 0.6e18
	assert accounts[0].balance() == account1_balance + 0.4e18

	account2_balance = accounts[1].balance()

	tx4 = FDT_contract.withdrawFunds({'from': accounts[1]})

	assert len(tx4.events) == 1
	assert tx4.events['FundsWithdrawn']['receiver'] == accounts[1]
	assert FDT_contract.balance() == 0.35e18
	assert accounts[1].balance() == account2_balance + 0.25e18

	account3_balance = accounts[2].balance()

	tx5 = FDT_contract.withdrawFunds({'from': accounts[2]})

	assert len(tx5.events) == 1
	assert tx5.events['FundsWithdrawn']['receiver'] == accounts[2]
	assert FDT_contract.balance() == 0
	assert accounts[2].balance() == account3_balance + 0.35e18