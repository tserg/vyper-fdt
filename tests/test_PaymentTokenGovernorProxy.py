import pytest

from brownie import (
	accounts,
	ERC20,
	PaymentTokenGovernor,
	PaymentTokenGovernorProxy,
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

@pytest.fixture(scope="module", autouse=True)
def NewPaymentTokenGovernorContract(PaymentTokenGovernor, accounts):
	yield PaymentTokenGovernor.deploy({'from': accounts[0]})

@pytest.fixture(scope="module", autouse=True)
def PaymentTokenGovernorProxyContract(PaymentTokenGovernorContract, accounts):
	yield PaymentTokenGovernorProxy.deploy(PaymentTokenGovernorContract, {'from': accounts[0]})

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
	pass

def test_initial_state(PaymentTokenGovernorContract, accounts):

	assert PaymentTokenGovernorContract.acceptedPaymentTokenCount() == 0

def test_add_payment_token_to_first_governor(PaymentTokenGovernorProxyContract, PaymentTokenGovernorContract, PaymentToken, accounts):

	tx1 = PaymentTokenGovernorContract.add_payment_token(PaymentToken.address, {'from': accounts[0]})

	assert tx1.events['PaymentTokenAdded']['paymentTokenAddress'] == PaymentToken.address
	assert PaymentTokenGovernorContract.acceptedPaymentTokenCount() == 1
	assert PaymentTokenGovernorContract.acceptedPaymentTokens(1) == PaymentToken.address
	assert PaymentTokenGovernorContract.paymentTokenToIndex(PaymentToken.address) == 1

	assert PaymentTokenGovernorProxyContract.acceptedPaymentTokenCount() == 1
	assert PaymentTokenGovernorProxyContract.acceptedPaymentTokens(1) == PaymentToken.address
	assert PaymentTokenGovernorProxyContract.paymentTokenToIndex(PaymentToken.address) == 1
	assert PaymentTokenGovernorProxyContract.check_payment_token_acceptance(PaymentToken.address) == True


def test_add_two_payment_tokens_to_first_governor(PaymentTokenGovernorProxyContract, PaymentTokenGovernorContract, PaymentToken, NewPaymentToken, accounts):

	tx1 = PaymentTokenGovernorContract.add_payment_token(PaymentToken.address, {'from': accounts[0]})

	assert tx1.events['PaymentTokenAdded']['paymentTokenAddress'] == PaymentToken.address
	assert PaymentTokenGovernorContract.acceptedPaymentTokenCount() == 1
	assert PaymentTokenGovernorContract.acceptedPaymentTokens(1) == PaymentToken.address
	assert PaymentTokenGovernorContract.paymentTokenToIndex(PaymentToken.address) == 1

	assert PaymentTokenGovernorProxyContract.acceptedPaymentTokenCount() == 1
	assert PaymentTokenGovernorProxyContract.acceptedPaymentTokens(1) == PaymentToken.address
	assert PaymentTokenGovernorProxyContract.paymentTokenToIndex(PaymentToken.address) == 1
	assert PaymentTokenGovernorProxyContract.check_payment_token_acceptance(PaymentToken.address) == True

	tx2 = PaymentTokenGovernorContract.add_payment_token(NewPaymentToken.address, {'from': accounts[0]})

	assert tx2.events['PaymentTokenAdded']['paymentTokenAddress'] == NewPaymentToken.address
	assert PaymentTokenGovernorContract.acceptedPaymentTokenCount() == 2
	assert PaymentTokenGovernorContract.acceptedPaymentTokens(2) == NewPaymentToken.address
	assert PaymentTokenGovernorContract.paymentTokenToIndex(NewPaymentToken.address) == 2

	assert PaymentTokenGovernorProxyContract.acceptedPaymentTokenCount() == 2
	assert PaymentTokenGovernorProxyContract.acceptedPaymentTokens(2) == NewPaymentToken.address
	assert PaymentTokenGovernorProxyContract.paymentTokenToIndex(NewPaymentToken.address) == 2
	assert PaymentTokenGovernorProxyContract.check_payment_token_acceptance(NewPaymentToken.address) == True


def test_add_two_and_remove_one_payment_token(PaymentTokenGovernorProxyContract, PaymentTokenGovernorContract, PaymentToken, NewPaymentToken, accounts):

	tx1 = PaymentTokenGovernorContract.add_payment_token(PaymentToken.address, {'from': accounts[0]})

	assert tx1.events['PaymentTokenAdded']['paymentTokenAddress'] == PaymentToken.address
	assert PaymentTokenGovernorContract.acceptedPaymentTokenCount() == 1
	assert PaymentTokenGovernorContract.acceptedPaymentTokens(1) == PaymentToken.address
	assert PaymentTokenGovernorContract.paymentTokenToIndex(PaymentToken.address) == 1

	assert PaymentTokenGovernorProxyContract.acceptedPaymentTokenCount() == 1
	assert PaymentTokenGovernorProxyContract.acceptedPaymentTokens(1) == PaymentToken.address
	assert PaymentTokenGovernorProxyContract.paymentTokenToIndex(PaymentToken.address) == 1
	assert PaymentTokenGovernorProxyContract.check_payment_token_acceptance(PaymentToken.address) == True

	tx2 = PaymentTokenGovernorContract.add_payment_token(NewPaymentToken.address, {'from': accounts[0]})

	assert tx2.events['PaymentTokenAdded']['paymentTokenAddress'] == NewPaymentToken.address
	assert PaymentTokenGovernorContract.acceptedPaymentTokenCount() == 2
	assert PaymentTokenGovernorContract.acceptedPaymentTokens(2) == NewPaymentToken.address
	assert PaymentTokenGovernorContract.paymentTokenToIndex(NewPaymentToken.address) == 2

	assert PaymentTokenGovernorProxyContract.acceptedPaymentTokenCount() == 2
	assert PaymentTokenGovernorProxyContract.acceptedPaymentTokens(2) == NewPaymentToken.address
	assert PaymentTokenGovernorProxyContract.paymentTokenToIndex(NewPaymentToken.address) == 2
	assert PaymentTokenGovernorProxyContract.check_payment_token_acceptance(NewPaymentToken.address) == True

	tx3 = PaymentTokenGovernorContract.remove_payment_token(PaymentToken.address, {'from': accounts[0]})

	assert tx3.events['PaymentTokenRemoved']['paymentTokenAddress'] == PaymentToken.address
	assert PaymentTokenGovernorContract.acceptedPaymentTokenCount() == 1
	assert PaymentTokenGovernorContract.acceptedPaymentTokens(2) == ZERO_ADDRESS
	assert PaymentTokenGovernorContract.paymentTokenToIndex(NewPaymentToken.address) == 1
	assert PaymentTokenGovernorContract.paymentTokenToIndex(PaymentToken.address) == 0

	assert PaymentTokenGovernorProxyContract.acceptedPaymentTokenCount() == 1
	assert PaymentTokenGovernorProxyContract.acceptedPaymentTokens(1) == NewPaymentToken.address
	assert PaymentTokenGovernorContract.acceptedPaymentTokens(2) == ZERO_ADDRESS
	assert PaymentTokenGovernorProxyContract.paymentTokenToIndex(NewPaymentToken.address) == 1
	assert PaymentTokenGovernorProxyContract.check_payment_token_acceptance(NewPaymentToken.address) == True
	assert PaymentTokenGovernorProxyContract.check_payment_token_acceptance(PaymentToken.address) == False
