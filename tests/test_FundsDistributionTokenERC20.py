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
def FDTERC20FactoryContract(FDTERC20Contract, FundsDistributionTokenERC20Factory, accounts):
	yield FundsDistributionTokenERC20Factory.deploy(FundsDistributionTokenERC20[0].address, accounts[0], {'from': accounts[0]})

@pytest.fixture(scope="module", autouse=True)
def test_deploy_fdt_from_factory(FDTERC20FactoryContract, ERC20, accounts):

	tx1 = FDTERC20FactoryContract.deploy_fdt_contract(TOKEN_NAME, TOKEN_SYMBOL, TOKEN_DECIMALS, TOKEN_SUPPLY, ERC20.address, {'from': accounts[0]})

	global FDT_INSTANCE
	FDT_INSTANCE = tx1.new_contracts[0]
	assert tx1.events[0]['name'] == TOKEN_NAME
	assert tx1.events[0]['symbol'] == TOKEN_SYMBOL

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
