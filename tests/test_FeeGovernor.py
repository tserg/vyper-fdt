import pytest

from brownie import (
	accounts,
	chain,
	reverts,
	FeeGovernor
)

@pytest.fixture(scope="module")
def FeeGovernorContract(FeeGovernor, accounts):
	yield FeeGovernor.deploy(1e16, {'from': accounts[0]})

@pytest.fixture(scope="module", autouse=True)
def test_commit_new_fee(FeeGovernorContract, accounts):

	tx1 = FeeGovernorContract.commit_new_admin_fee(2e16, {'from': accounts[0]})

	assert tx1.events['newAdminFeeCommitted']['new_admin_fee'] == 2e16

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
	pass


def test_initial_fee(FeeGovernorContract):

	assert FeeGovernorContract.admin_fee() == 1e16

def test_apply_new_fee(FeeGovernorContract, accounts):

	assert FeeGovernorContract.future_admin_fee() == 2e16

	with reverts():
		tx1 = FeeGovernorContract.apply_new_admin_fee({'from': accounts[0]})

	chain.sleep(259200)

	tx2 = FeeGovernorContract.apply_new_admin_fee({'from': accounts[0]})

	assert tx2.events['newAdminFeeApplied']['new_admin_fee'] == 2e16
	assert FeeGovernorContract.admin_fee() == 2e16