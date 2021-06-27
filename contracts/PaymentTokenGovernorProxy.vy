# @version ^0.2.0

event PaymentTokenGovernorUpdated:
	oldGovernor: indexed(address)
	newGovernor: indexed(address)

paymentTokenGovernorAddress: public(address)
admin: address

@external
def __init__(_paymentTokenGovernorAddress: address):
	self.paymentTokenGovernorAddress = _paymentTokenGovernorAddress
	self.admin = msg.sender

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

	log PaymentTokenGovernorUpdated(_previousPaymentTokenGovernorAddress, _address)
