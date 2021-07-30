import pytest

from brownie import (
	accounts,
	chain,
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

	assert PaymentTokenGovernorContract.accepted_payment_token_count() == 0

def test_add_payment_token_to_first_governor(PaymentTokenGovernorProxyContract, PaymentTokenGovernorContract, PaymentToken, accounts):

	tx1 = PaymentTokenGovernorContract.add_payment_token(PaymentToken.address, {'from': accounts[0]})

	assert tx1.events['PaymentTokenAdded']['paymentTokenAddress'] == PaymentToken.address
	assert PaymentTokenGovernorContract.accepted_payment_token_count() == 1
	assert PaymentTokenGovernorContract.accepted_payment_tokens(1) == PaymentToken.address
	assert PaymentTokenGovernorContract.payment_token_to_index(PaymentToken.address) == 1

	assert PaymentTokenGovernorProxyContract.get_accepted_payment_token_count() == 1
	assert PaymentTokenGovernorProxyContract.get_accepted_payment_tokens(1) == PaymentToken.address
	assert PaymentTokenGovernorProxyContract.get_payment_token_to_index(PaymentToken.address) == 1
	assert PaymentTokenGovernorProxyContract.get_payment_token_acceptance(PaymentToken.address) == True


def test_add_two_payment_tokens_to_first_governor(PaymentTokenGovernorProxyContract, PaymentTokenGovernorContract, PaymentToken, NewPaymentToken, accounts):

	tx1 = PaymentTokenGovernorContract.add_payment_token(PaymentToken.address, {'from': accounts[0]})

	assert tx1.events['PaymentTokenAdded']['paymentTokenAddress'] == PaymentToken.address
	assert PaymentTokenGovernorContract.accepted_payment_token_count() == 1
	assert PaymentTokenGovernorContract.accepted_payment_tokens(1) == PaymentToken.address
	assert PaymentTokenGovernorContract.payment_token_to_index(PaymentToken.address) == 1

	assert PaymentTokenGovernorProxyContract.get_accepted_payment_token_count() == 1
	assert PaymentTokenGovernorProxyContract.get_accepted_payment_tokens(1) == PaymentToken.address
	assert PaymentTokenGovernorProxyContract.get_payment_token_to_index(PaymentToken.address) == 1
	assert PaymentTokenGovernorProxyContract.get_payment_token_acceptance(PaymentToken.address) == True

	tx2 = PaymentTokenGovernorContract.add_payment_token(NewPaymentToken.address, {'from': accounts[0]})

	assert tx2.events['PaymentTokenAdded']['paymentTokenAddress'] == NewPaymentToken.address
	assert PaymentTokenGovernorContract.accepted_payment_token_count() == 2
	assert PaymentTokenGovernorContract.accepted_payment_tokens(2) == NewPaymentToken.address
	assert PaymentTokenGovernorContract.payment_token_to_index(NewPaymentToken.address) == 2

	assert PaymentTokenGovernorProxyContract.get_accepted_payment_token_count() == 2
	assert PaymentTokenGovernorProxyContract.get_accepted_payment_tokens(2) == NewPaymentToken.address
	assert PaymentTokenGovernorProxyContract.get_payment_token_to_index(NewPaymentToken.address) == 2
	assert PaymentTokenGovernorProxyContract.get_payment_token_acceptance(NewPaymentToken.address) == True


def test_add_two_and_remove_one_payment_token(PaymentTokenGovernorProxyContract, PaymentTokenGovernorContract, PaymentToken, NewPaymentToken, accounts):

	tx1 = PaymentTokenGovernorContract.add_payment_token(PaymentToken.address, {'from': accounts[0]})

	assert tx1.events['PaymentTokenAdded']['paymentTokenAddress'] == PaymentToken.address
	assert PaymentTokenGovernorContract.accepted_payment_token_count() == 1
	assert PaymentTokenGovernorContract.accepted_payment_tokens(1) == PaymentToken.address
	assert PaymentTokenGovernorContract.payment_token_to_index(PaymentToken.address) == 1

	assert PaymentTokenGovernorProxyContract.get_accepted_payment_token_count() == 1
	assert PaymentTokenGovernorProxyContract.get_accepted_payment_tokens(1) == PaymentToken.address
	assert PaymentTokenGovernorProxyContract.get_payment_token_to_index(PaymentToken.address) == 1
	assert PaymentTokenGovernorProxyContract.get_payment_token_acceptance(PaymentToken.address) == True

	tx2 = PaymentTokenGovernorContract.add_payment_token(NewPaymentToken.address, {'from': accounts[0]})

	assert tx2.events['PaymentTokenAdded']['paymentTokenAddress'] == NewPaymentToken.address
	assert PaymentTokenGovernorContract.accepted_payment_token_count() == 2
	assert PaymentTokenGovernorContract.accepted_payment_tokens(2) == NewPaymentToken.address
	assert PaymentTokenGovernorContract.payment_token_to_index(NewPaymentToken.address) == 2

	assert PaymentTokenGovernorProxyContract.get_accepted_payment_token_count() == 2
	assert PaymentTokenGovernorProxyContract.get_accepted_payment_tokens(2) == NewPaymentToken.address
	assert PaymentTokenGovernorProxyContract.get_payment_token_to_index(NewPaymentToken.address) == 2
	assert PaymentTokenGovernorProxyContract.get_payment_token_acceptance(NewPaymentToken.address) == True

	tx3 = PaymentTokenGovernorContract.commit_remove_payment_token(PaymentToken.address, {'from': accounts[0]})
	chain.sleep(259200)
	tx4 = PaymentTokenGovernorContract.apply_remove_payment_token({'from': accounts[0]})

	assert tx4.events['PaymentTokenRemoved']['paymentTokenAddress'] == PaymentToken.address
	assert PaymentTokenGovernorContract.accepted_payment_token_count() == 1
	assert PaymentTokenGovernorContract.accepted_payment_tokens(2) == ZERO_ADDRESS
	assert PaymentTokenGovernorContract.payment_token_to_index(NewPaymentToken.address) == 1
	assert PaymentTokenGovernorContract.payment_token_to_index(PaymentToken.address) == 0

	assert PaymentTokenGovernorProxyContract.get_accepted_payment_token_count() == 1
	assert PaymentTokenGovernorProxyContract.get_accepted_payment_tokens(1) == NewPaymentToken.address
	assert PaymentTokenGovernorProxyContract.get_accepted_payment_tokens(2) == ZERO_ADDRESS
	assert PaymentTokenGovernorProxyContract.get_payment_token_to_index(NewPaymentToken.address) == 1
	assert PaymentTokenGovernorProxyContract.get_payment_token_acceptance(NewPaymentToken.address) == True
	assert PaymentTokenGovernorProxyContract.get_payment_token_acceptance(PaymentToken.address) == False
