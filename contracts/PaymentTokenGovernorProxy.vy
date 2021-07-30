# @version ^0.2.0

interface PaymentTokenGovernor:
	def check_payment_token_acceptance(
		_paymentTokenAddress: address
	) -> bool: view

	def accepted_payment_token_count() -> uint256: view

	def accepted_payment_tokens(
		_index: uint256
	) -> address: view

	def payment_token_to_index(
		_paymentTokenAddress: address
	) -> uint256: view

event PaymentTokenGovernorUpdated:
	oldGovernor: indexed(address)
	newGovernor: indexed(address)

payment_token_governor_address: public(address)
current_payment_token_governor: PaymentTokenGovernor
admin: address

@external
def __init__(_payment_token_governor_address: address):
	self.payment_token_governor_address = _payment_token_governor_address
	self.admin = msg.sender
	self.current_payment_token_governor = PaymentTokenGovernor(_payment_token_governor_address)

@external
def set_payment_token_governor(_address: address):
	"""
	@notice Set the payment token governor address for FDT contracts
	@param _address Address of the payment token governer
	"""
	# Check that caller is admin
	assert msg.sender == self.admin
	_previouspayment_token_governor_address: address = self.payment_token_governor_address

	self.payment_token_governor_address = _address
	self.current_payment_token_governor = PaymentTokenGovernor(_address)

	log PaymentTokenGovernorUpdated(_previouspayment_token_governor_address, _address)

@external
@view
def check_payment_token_acceptance(_paymentTokenAddress: address) -> bool:
	"""
	@dev Function to check if payment token is accepted by current PaymentTokenGovernor
	@return Boolean value indicating True if payment token is accepted. Otherwise, False.
	"""
	return self.current_payment_token_governor.check_payment_token_acceptance(_paymentTokenAddress)

@external
@view
def get_accepted_payment_token_count() -> uint256:
	"""
	@dev Get count of accepted payment tokens from current PaymentTokenGovernor
	@return Integer value for number of payment tokens accepted
	"""
	return self.current_payment_token_governor.accepted_payment_token_count()

@external
@view
def get_accepted_payment_tokens(_index: uint256) -> address:
	"""
	@dev Get accepted payment token by index from current PaymentTokenGovernor
	@return Address of payment token at given index
	"""
	return self.current_payment_token_governor.accepted_payment_tokens(_index)

@external
@view
def get_payment_token_to_index(_paymentTokenAddress: address) -> uint256:
	"""
	@dev Get index of a payment token from current PaymentTokenGovernor
	@return Given index of payment token in current PaymentTokenGovernor. Returns 0 if it does not exist.
	"""
	return self.current_payment_token_governor.payment_token_to_index(_paymentTokenAddress)
