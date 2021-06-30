# @version ^0.2.0

interface PaymentTokenGovernor:
	def check_payment_token_acceptance(
		_paymentTokenAddress: address
	) -> bool: view

	def acceptedPaymentTokenCount() -> uint256: view

	def acceptedPaymentTokens(
		_index: uint256
	) -> address: view

	def paymentTokenToIndex(
		_paymentTokenAddress: address
	) -> uint256: view

event PaymentTokenGovernorUpdated:
	oldGovernor: indexed(address)
	newGovernor: indexed(address)

paymentTokenGovernorAddress: public(address)
currentPaymentTokenGovernor: PaymentTokenGovernor
admin: address

@external
def __init__(_paymentTokenGovernorAddress: address):
	self.paymentTokenGovernorAddress = _paymentTokenGovernorAddress
	self.admin = msg.sender
	self.currentPaymentTokenGovernor = PaymentTokenGovernor(_paymentTokenGovernorAddress)

@external
def set_payment_token_governor(_address: address):
	"""
	@notice Set the payment token governor address for FDT contracts
	@param _address Address of the payment token governer
	"""
	# Check that caller is admin
	assert msg.sender == self.admin
	_previousPaymentTokenGovernorAddress: address = self.paymentTokenGovernorAddress

	self.paymentTokenGovernorAddress = _address
	self.currentPaymentTokenGovernor = PaymentTokenGovernor(_address)

	log PaymentTokenGovernorUpdated(_previousPaymentTokenGovernorAddress, _address)

@external
@view
def check_payment_token_acceptance(_paymentTokenAddress: address) -> bool:
	"""
	@dev Function to check if payment token is accepted by current PaymentTokenGovernor
	@return Boolean value indicating True if payment token is accepted. Otherwise, False.
	"""
	return self.currentPaymentTokenGovernor.check_payment_token_acceptance(_paymentTokenAddress)

@external
@view
def acceptedPaymentTokenCount() -> uint256:
	"""
	@dev Get count of accepted payment tokens from current PaymentTokenGovernor
	@return Integer value for number of payment tokens accepted
	"""
	return self.currentPaymentTokenGovernor.acceptedPaymentTokenCount()

@external
@view
def acceptedPaymentTokens(_index: uint256) -> address:
	"""
	@dev Get accepted payment token by index from current PaymentTokenGovernor
	@return Address of payment token at given index
	"""
	return self.currentPaymentTokenGovernor.acceptedPaymentTokens(_index)

@external
@view
def paymentTokenToIndex(_paymentTokenAddress: address) -> uint256:
	"""
	@dev Get index of a payment token from current PaymentTokenGovernor
	@return Given index of payment token in current PaymentTokenGovernor. Returns 0 if it does not exist.
	"""
	return self.currentPaymentTokenGovernor.paymentTokenToIndex(_paymentTokenAddress)
