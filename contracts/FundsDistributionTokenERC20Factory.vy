# @version ^0.3.0

"""
@title Funds Distribution Token Factory
@author Gary Tse
@notice Factory to deploy 'FundsDistributionTokenERC20' contracts
"""

interface FundsDistributionToken:
	def initialize(
		_name: String[64],
		_symbol: String[32],
		_decimals: uint256,
		_supply: uint256,
		_ownerAddress: address,
		_paymentTokenAddress: address
	) -> bool: nonpayable

event FundsDistributionTokenCreated:
	fundsId: uint256
	token: address
	name: String[64]
	symbol: String[32]

event PaymentTokenUpdated:
	previousPaymentToken: address
	newPaymentToken: address

admin: public(address)
target: public(address)
fundsId: public(uint256)
fundsIdToAddress: public(HashMap[uint256, address])
paymentTokenAddress: public(address)

@external
def __init__(_target: address, _admin: address, _paymentTokenAddress: address):
	"""
	@notice Constructor
	@param _target 'FundsDistributionToken' contract address
	"""
	self.target = _target
	self.admin = _admin
	self.fundsId = 0
	self.paymentTokenAddress = _paymentTokenAddress

@external
def deploy_fdt_contract(
	_name: String[64],
	_symbol: String[32],
	_decimals: uint256,
	_supply: uint256
) -> address:
	"""
	@notice Deploy a funds distribution token contract
	@param _name Name of the funds distribution token
	@param _symbol Symbol of the funds distribution token
	@param _decimals Number of decimals for the funds distribution token
	@param _supply Total supply of the funds distribution token
	"""

	#assert msg.sender == self.admin

	_contract: address = create_forwarder_to(self.target)
	FundsDistributionToken(_contract).initialize(
		_name,
		_symbol,
		_decimals,
		_supply,
		msg.sender,
		self.paymentTokenAddress
	)
	self.fundsId += 1
	self.fundsIdToAddress[self.fundsId] = _contract
	log FundsDistributionTokenCreated(self.fundsId, _contract, _name, _symbol)
	return _contract

@external
def set_payment_token(_token: address):
	"""
	@notice Set the payment token address for FDT contracts
	@param _token Address of the payment token
	"""
	# Check that caller is admin
	assert msg.sender == self.admin
	_previousPaymentTokenAddress: address = self.paymentTokenAddress

	self.paymentTokenAddress = _token

	log PaymentTokenUpdated(_previousPaymentTokenAddress, _token)
