# @version ^0.2.0

# @dev Contract to add payment tokens for FundsDistributionTokenMultiERC20
# @author Gary Tse (@tserg)

from vyper.interfaces import ERC20

event PaymentTokenAdded:
	paymentTokenAddress: indexed(address)

event RemovePaymentTokenCommitted:
	paymentTokenAddress: indexed(address)

event PaymentTokenRemoved:
	paymentTokenAddress: indexed(address)

admin: address

ADMIN_ACTIONS_DELAY: constant(uint256) = 3 * 86400

# @dev Mapping of payment token to whether it is accepted
payment_tokens: public(HashMap[address, bool])

# @dev Mapping of index to accepted payment tokens
accepted_payment_tokens: public(HashMap[uint256, address])

# @dev Mapping of payment token to current index in accepted_payment_tokens
payment_token_to_index: public(HashMap[address, uint256])

# @dev Count of number of accepted tokens
accepted_payment_token_count: public(uint256)

# @dev Mapping of payment token committed for removal to admin action deadline
admin_remove_payment_token_deadline: HashMap[address, uint256]

# @dev Maximum number of payment tokens to be added to governor
max_payment_tokens: uint256
MAX_PAYMENT_TOKENS: constant(uint256) = 10

@external
def __init__():
	"""
	@notice Constructor
	"""
	self.admin = msg.sender
	self.accepted_payment_token_count = 0
	self.max_payment_tokens = MAX_PAYMENT_TOKENS

@external
def add_payment_token(_payment_token: address):
	"""
	@dev Function to add a payment token
    @param _payment_token The address of the payment token to be added
	"""
	assert msg.sender == self.admin
	assert self.accepted_payment_token_count < self.max_payment_tokens

	self.payment_tokens[_payment_token] = True
	self.accepted_payment_token_count += 1
	self.accepted_payment_tokens[self.accepted_payment_token_count] = _payment_token
	self.payment_token_to_index[_payment_token] = self.accepted_payment_token_count

	log PaymentTokenAdded(_payment_token)

@external
def commit_remove_payment_token(_payment_token: address):
	"""
	@notice Remove payment token
	@param _payment_token Address of payment token to be removed
	"""
	assert msg.sender == self.admin
	assert self.payment_tokens[_payment_token] == True
	assert self.payment_token_to_index[_payment_token] != 0

	deadline: uint256 = block.timestamp + ADMIN_ACTIONS_DELAY

	self.admin_remove_payment_token_deadline[_payment_token] = deadline

	log RemovePaymentTokenCommitted(_payment_token)

@internal
def _remove_payment_token(_payment_token: address):
	"""
	@dev Function to remove a payment token
	@param _payment_token The address of the payment token to be removed
	"""

	self.payment_tokens[_payment_token] = False

	# Get index of last payment token to swap
	_currentPaymentTokenIndex: uint256 = self.payment_token_to_index[_payment_token]

	# Get last payment token
	_lastPaymentToken: address = self.accepted_payment_tokens[self.accepted_payment_token_count]

	if self.accepted_payment_token_count == _currentPaymentTokenIndex:
		# Set last index to ZERO_ADDRESS
		self.accepted_payment_tokens[_currentPaymentTokenIndex] = ZERO_ADDRESS

	else:

		# Swap position of current payment token and last payment token if payment token to be removed
		# is not the last index
		self.accepted_payment_tokens[_currentPaymentTokenIndex] = _lastPaymentToken
		self.accepted_payment_tokens[self.accepted_payment_token_count] = ZERO_ADDRESS
		self.payment_token_to_index[_lastPaymentToken] = _currentPaymentTokenIndex

	# Set index of payment token to be removed to 0
	self.payment_token_to_index[_payment_token] = 0

	# Set last payment token to ZERO_ADDRESS
	self.accepted_payment_token_count -= 1

	# Set admin action deadline for payment token to 0
	self.admin_remove_payment_token_deadline[_payment_token] = 0

	log PaymentTokenRemoved(_payment_token)

@external
def apply_remove_payment_token():
	"""
	@notice Remove all payment tokens that have been committed for removal
	"""
	for i in range(10):

		if i > self.max_payment_tokens:
			break

		_payment_token: address = self.accepted_payment_tokens[i]
		_payment_token_remove_deadline: uint256 = self.admin_remove_payment_token_deadline[_payment_token]

		if _payment_token_remove_deadline == 0:
			continue

		if _payment_token_remove_deadline > 0 and block.timestamp >= _payment_token_remove_deadline:
			self._remove_payment_token(_payment_token)


@view
@external
def get_payment_token_acceptance(_payment_token: address) -> bool:
	"""
	@dev Function to check if payment token is accepted
	@return Boolean value indicating True if payment token is accepted. Otherwise, False.
	"""
	return self.payment_tokens[_payment_token]
