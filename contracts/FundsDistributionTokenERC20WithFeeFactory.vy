# @version ^0.2.0

"""
@title Funds Distribution Token Factory
@author Gary Tse
@notice Factory to deploy 'FundsDistributionTokens' contracts
"""

interface FundsDistributionTokenERC20WithFee:
	def initialize(
		_name: String[64],
		_symbol: String[32],
		_decimals: uint256,
		_supply: uint256,
		_ownerAddress: address,
		_paymentTokenAddress: address,
		_feeGovernor: address
	) -> bool: nonpayable

event FundsDistributionTokenCreated:
	fundsId: uint256
	token: address
	name: String[64]
	symbol: String[32]

event PaymentTokenUpdated:
	previousPaymentToken: address
	newPaymentToken: address

event FeeGovernorUpdated:
	previousFeeGovernor: address
	newFeeGovernor: address

# @dev Address of admin
admin: public(address)

# @dev Address of FundsDistributionTokenERC20WithFee contract
target: public(address)

# @dev Count of deployed FundsDistributionTokenERC20WithFee instances
funds_id: public(uint256)

# @dev Mapping of fund ID to address of deployed FundsDistributionTokenERC20WithFee instance
funds_id_to_address: public(HashMap[uint256, address])

# @dev Address of payment token
payment_token_address: public(address)

# @dev Address of FeeGovernorProxy
fee_governor_address: public(address)

@external
def __init__(
	_target: address,
	_admin: address,
	_payment_token_address: address,
	_fee_governor_address: address
):
	"""
	@notice Constructor
	@param _target 'FundsDistributionTokenERC20WithFee' contract address
	@param _admin Address of admin
	@param _payment_token_address Address of payment token
	@param _fee_governor_address Address of FeeGovernor
	"""
	self.target = _target
	self.admin = _admin
	self.funds_id = 0
	self.payment_token_address = _payment_token_address
	self.fee_governor_address = _fee_governor_address

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
	FundsDistributionTokenERC20WithFee(_contract).initialize(
		_name,
		_symbol,
		_decimals,
		_supply,
		msg.sender,
		self.payment_token_address,
		self.fee_governor_address
	)
	self.funds_id += 1
	self.funds_id_to_address[self.funds_id] = _contract
	log FundsDistributionTokenCreated(self.funds_id, _contract, _name, _symbol)
	return _contract
