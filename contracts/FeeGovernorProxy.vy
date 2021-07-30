# @version ^0.2.0

interface FeeGovernor:
	def admin_fee() -> uint256: view

	def future_admin_fee() -> uint256: view

	def beneficiary() -> address: view

	def future_beneficiary() -> address: view

event NewFeeGovernorCommitted:
	newGovernor: indexed(address)

event FeeGovernorUpdated:
	oldGovernor: indexed(address)
	newGovernor: indexed(address)

ADMIN_ACTIONS_DELAY: constant(uint256) = 3 * 86400

fee_governor_address: public(address)
future_fee_governor_address: public(address)

current_fee_governor: FeeGovernor
admin: address

# @dev Admin action deadline
admin_change_fee_governor_deadline: uint256

@external
def __init__(_fee_governor_address: address):
	self.fee_governor_address = _fee_governor_address
	self.admin = msg.sender
	self.current_fee_governor = FeeGovernor(_fee_governor_address)

@external
def commit_change_fee_governor(_address: address):
	"""
	@notice Set the fee governor address for FDT contracts
	@param _address Address of the fee governer
	"""
	# Check that caller is admin
	assert msg.sender == self.admin
	assert self.future_fee_governor_address == ZERO_ADDRESS
	assert self.admin_change_fee_governor_deadline == 0

	_previous_fee_governor__address: address = self.fee_governor_address

	_deadline: uint256 = block.timestamp + ADMIN_ACTIONS_DELAY

	self.future_fee_governor_address = _address
	self.admin_change_fee_governor_deadline = _deadline

	self.future_fee_governor_address = _address


	log NewFeeGovernorCommitted(_address)

@external
def apply_change_fee_governor():
	"""
	@notice Change to the future fee governor address for FDT contracts
	"""
	# Check that caller is admin
	assert msg.sender == self.admin
	assert block.timestamp >= self.admin_change_fee_governor_deadline

	_previous_fee_governor_address: address = self.fee_governor_address

	self.fee_governor_address = self.future_fee_governor_address
	self.current_fee_governor = FeeGovernor(self.fee_governor_address)
	self.future_fee_governor_address = ZERO_ADDRESS
	self.admin_change_fee_governor_deadline = 0

	log FeeGovernorUpdated(_previous_fee_governor_address, self.fee_governor_address)

@external
@view
def get_admin_fee() -> uint256:
	"""
	@notice Get admin fee of current fee governor
	@return Integer value of current admin fee
	"""
	return self.current_fee_governor.admin_fee()

@external
@view
def get_future_admin_fee() -> uint256:
	"""
	@notice Get future admin fee of current fee governor
	@return Integer value of future admin fee
	"""
	return self.current_fee_governor.future_admin_fee()

@external
@view
def get_beneficiary() -> address:
	"""
	@notice Get beneficiary address of current fee governor
	@return Address of beneficiary
	"""
	return self.current_fee_governor.beneficiary()

@external
@view
def get_future_beneficiary() -> address:
	"""
	@notice Get future beneficiary address of current fee governor
	@return Address of future beneficiary
	"""
	return self.current_fee_governor.future_beneficiary()
