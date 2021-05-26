from brownie import (
	FundsDistributionToken,
	accounts,
)

def main():
	acct = accounts.load('deployment_account')
	FundsDistributionToken.deploy('Musicakes', 'MCAKES', 0, 100, {'from': acct})
