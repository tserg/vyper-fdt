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