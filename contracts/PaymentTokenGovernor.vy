# @version ^0.2.0

# @dev Contract to add payment tokens for FundsDistributionTokenMultiERC20
# @author Gary Tse (@tserg)

from vyper.interfaces import ERC20

event PaymentTokenAdded:
	paymentTokenAddress: indexed(address)

event PaymentTokenRemoved:
	paymentTokenAddress: indexed(address)

admin: address

# @dev Mapping of payment token to whether it is accepted
paymentTokens: public(HashMap[address, bool])

# @dev Mapping of index to accepted payment tokens
acceptedPaymentTokens: public(HashMap[uint256, address])

# @dev Mapping of payment token to current index in acceptedPaymentTokens
paymentTokenToIndex: public(HashMap[address, uint256])

# @dev Count of number of accepted tokens
acceptedPaymentTokenCount: public(uint256)

@external
def __init__():
	"""
	@notice Constructor
	"""
	self.admin = msg.sender
	self.acceptedPaymentTokenCount = 0

@external
def add_payment_token(_paymentTokenAddress: address):
	"""
	@dev Function to add a payment token
    @param _paymentTokenAddress The address of the payment token to be added
	"""
	assert msg.sender == self.admin

	self.paymentTokens[_paymentTokenAddress] = True
	self.acceptedPaymentTokenCount += 1
	self.acceptedPaymentTokens[self.acceptedPaymentTokenCount] = _paymentTokenAddress
	self.paymentTokenToIndex[_paymentTokenAddress] = self.acceptedPaymentTokenCount

	log PaymentTokenAdded(_paymentTokenAddress)

@external
def remove_payment_token(_paymentTokenAddress: address):
	"""
	@dev Function to remove a payment token
	@param _paymentTokenAddress The address of the payment token to be removed
	"""
	assert msg.sender == self.admin

	assert self.paymentTokens[_paymentTokenAddress] == True
	assert self.paymentTokenToIndex[_paymentTokenAddress] != 0

	self.paymentTokens[_paymentTokenAddress] = False

	# Get index of last payment token to swap
	_currentPaymentTokenIndex: uint256 = self.paymentTokenToIndex[_paymentTokenAddress]

	# Get last payment token
	_lastPaymentToken: address = self.acceptedPaymentTokens[self.acceptedPaymentTokenCount]

	# Swap position of current payment token and last payment token
	self.acceptedPaymentTokens[_currentPaymentTokenIndex] = _lastPaymentToken
	self.acceptedPaymentTokens[self.acceptedPaymentTokenCount] = ZERO_ADDRESS

	self.paymentTokenToIndex[_paymentTokenAddress] = 0
	self.paymentTokenToIndex[_lastPaymentToken] = _currentPaymentTokenIndex

	# Set last payment token to ZERO_ADDRESS
	self.acceptedPaymentTokenCount -= 1

	log PaymentTokenRemoved(_paymentTokenAddress)

@view
@external
def check_payment_token_acceptance(_paymentTokenAddress: address) -> bool:
	"""
	@dev Function to check if payment token is accepted
	@return Boolean value indicating True if payment token is accepted. Otherwise, False.
	"""
	return self.paymentTokens[_paymentTokenAddress]
