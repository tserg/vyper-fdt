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

	tx2 = FDT_contract.payToContract({'from': accounts[0], 'amount': 1e18})

	assert FDT_contract.balance() == 1e18

	tx1 = FDT_contract.withdrawFunds({'from': accounts[0]})

	assert len(tx1.events) == 2
	assert tx1.events['FundsDistributed']['receiver'] == accounts[0]
	assert tx1.events['FundsWithdrawn']['receiver'] == accounts[0]
	assert FDT_contract.balance() == 0