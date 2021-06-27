import pytest

from brownie import (
	accounts,
	ERC20,
	PaymentTokenGovernor
)

PAYMENT_TOKEN_NAME = "Sai"
PAYMENT_TOKEN_SYMBOL = "SAI"
PAYMENT_TOKEN_DECIMALS = 18
PAYMENT_TOKEN_SUPPLY = 1000

NEW_PAYMENT_TOKEN_NAME = "Dai"
NEW_PAYMENT_TOKEN_SYMBOL = "DAI"
NEW_PAYMENT_TOKEN_DECIMALS = 18
NEW_PAYMENT_TOKEN_SUPPLY = 1000

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

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
	pass

def test_initial_state(PaymentTokenGovernorContract, accounts):

	assert PaymentTokenGovernorContract.acceptedPaymentTokenCount() == 0

def test_add_payment_token(PaymentTokenGovernorContract, PaymentToken, accounts):

	tx1 = PaymentTokenGovernorContract.add_payment_token(PaymentToken.address, {'from': accounts[0]})

	assert tx1.events['PaymentTokenAdded']['paymentTokenAddress'] == PaymentToken.address
	assert PaymentTokenGovernorContract.acceptedPaymentTokenCount() == 1
	assert PaymentTokenGovernorContract.acceptedPaymentTokens(1) == PaymentToken.address
	assert PaymentTokenGovernorContract.paymentTokenToIndex(PaymentToken.address) == 1

def test_add_two_payment_tokens(PaymentTokenGovernorContract, PaymentToken, NewPaymentToken, accounts):

	tx1 = PaymentTokenGovernorContract.add_payment_token(PaymentToken.address, {'from': accounts[0]})

	assert tx1.events['PaymentTokenAdded']['paymentTokenAddress'] == PaymentToken.address
	assert PaymentTokenGovernorContract.acceptedPaymentTokenCount() == 1
	assert PaymentTokenGovernorContract.acceptedPaymentTokens(1) == PaymentToken.address
	assert PaymentTokenGovernorContract.paymentTokenToIndex(PaymentToken.address) == 1

	tx2 = PaymentTokenGovernorContract.add_payment_token(NewPaymentToken.address, {'from': accounts[0]})

	assert tx2.events['PaymentTokenAdded']['paymentTokenAddress'] == NewPaymentToken.address
	assert PaymentTokenGovernorContract.acceptedPaymentTokenCount() == 2
	assert PaymentTokenGovernorContract.acceptedPaymentTokens(2) == NewPaymentToken.address
	assert PaymentTokenGovernorContract.paymentTokenToIndex(NewPaymentToken.address) == 2

def test_add_two_and_remove_one_payment_token(PaymentTokenGovernorContract, PaymentToken, NewPaymentToken, accounts):

	tx1 = PaymentTokenGovernorContract.add_payment_token(PaymentToken.address, {'from': accounts[0]})

	assert tx1.events['PaymentTokenAdded']['paymentTokenAddress'] == PaymentToken.address
	assert PaymentTokenGovernorContract.acceptedPaymentTokenCount() == 1
	assert PaymentTokenGovernorContract.acceptedPaymentTokens(1) == PaymentToken.address
	assert PaymentTokenGovernorContract.paymentTokenToIndex(PaymentToken.address) == 1

	tx2 = PaymentTokenGovernorContract.add_payment_token(NewPaymentToken.address, {'from': accounts[0]})

	assert tx2.events['PaymentTokenAdded']['paymentTokenAddress'] == NewPaymentToken.address
	assert PaymentTokenGovernorContract.acceptedPaymentTokenCount() == 2
	assert PaymentTokenGovernorContract.acceptedPaymentTokens(2) == NewPaymentToken.address
	assert PaymentTokenGovernorContract.paymentTokenToIndex(NewPaymentToken.address) == 2

	tx3 = PaymentTokenGovernorContract.remove_payment_token(PaymentToken.address, {'from': accounts[0]})

	assert tx3.events['PaymentTokenRemoved']['paymentTokenAddress'] == PaymentToken.address
	assert PaymentTokenGovernorContract.acceptedPaymentTokenCount() == 1
	assert PaymentTokenGovernorContract.acceptedPaymentTokens(2) == ZERO_ADDRESS
	assert PaymentTokenGovernorContract.paymentTokenToIndex(NewPaymentToken.address) == 1
	assert PaymentTokenGovernorContract.paymentTokenToIndex(PaymentToken.address) == 0
