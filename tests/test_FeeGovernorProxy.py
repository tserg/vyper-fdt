import pytest

from brownie import (
	accounts,
	chain,
	reverts,
	FeeGovernor,
	FeeGovernorProxy,
)

@pytest.fixture(scope="module")
def FeeGovernorContract(FeeGovernor, accounts):
	yield FeeGovernor.deploy(1e8, {'from': accounts[0]})

@pytest.fixture(scope="module")
def NewFeeGovernorContract(FeeGovernor, accounts):
	yield FeeGovernor.deploy(3e8, {'from': accounts[0]})

@pytest.fixture(scope="module", autouse=True)
def FeeGovernorProxyContract(FeeGovernorContract, accounts):
	yield FeeGovernorProxy.deploy(FeeGovernorContract, {'from': accounts[0]})

@pytest.fixture(scope="module", autouse=True)
def test_commit_new_fee(FeeGovernorContract, accounts):

	tx1 = FeeGovernorContract.commit_new_admin_fee(2e8, {'from': accounts[0]})

	assert tx1.events['newAdminFeeCommitted']['new_admin_fee'] == 2e8

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
	pass


def test_initial_fee(FeeGovernorContract, FeeGovernorProxyContract):

	assert FeeGovernorContract.admin_fee() == 1e8
	assert FeeGovernorProxyContract.get_admin_fee() == 1e8
	assert FeeGovernorProxyContract.get_future_admin_fee() == 2e8


def test_apply_new_fee(FeeGovernorContract, FeeGovernorProxyContract, accounts):

	assert FeeGovernorContract.future_admin_fee() == 2e8

	with reverts():
		tx1 = FeeGovernorContract.apply_new_admin_fee({'from': accounts[0]})

	chain.sleep(259200)

	tx2 = FeeGovernorContract.apply_new_admin_fee({'from': accounts[0]})

	assert tx2.events['newAdminFeeApplied']['new_admin_fee'] == 2e8
	assert FeeGovernorContract.admin_fee() == 2e8
	assert FeeGovernorProxyContract.get_admin_fee() == 2e8

def test_initial_beneficiary(FeeGovernorContract, FeeGovernorProxyContract, accounts):

	assert FeeGovernorContract.beneficiary() == accounts[0]
	assert FeeGovernorProxyContract.get_beneficiary() == accounts[0]

def test_commit_and_apply_new_beneficiary(FeeGovernorContract, FeeGovernorProxyContract, accounts):

	tx1 = FeeGovernorContract.commit_new_beneficiary(accounts[1], {'from': accounts[0]})

	assert tx1.events['newBeneficiaryCommitted']['beneficiary'] == accounts[1]
	assert FeeGovernorContract.future_beneficiary() == accounts[1]
	assert FeeGovernorContract.beneficiary() == accounts[0]

	assert FeeGovernorProxyContract.get_future_beneficiary() == accounts[1]
	assert FeeGovernorProxyContract.get_beneficiary() == accounts[0]

	with reverts():
		tx2 = FeeGovernorContract.apply_new_beneficiary({'from': accounts[0]})

	chain.sleep(259200)

	tx3 = FeeGovernorContract.apply_new_beneficiary({'from': accounts[0]})

	assert tx3.events['newBeneficiaryApplied']['beneficiary'] == accounts[1]
	assert FeeGovernorContract.beneficiary() == accounts[1]

	assert FeeGovernorProxyContract.get_beneficiary() == accounts[1]
