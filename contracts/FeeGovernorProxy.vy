# @version ^0.2.0

interface FeeGovernor:
	def check_payment_token_acceptance(
		_paymentTokenAddress: address
	) -> bool: view

	def admin_fee() -> uint256: view

	def future_admin_fee() -> uint256: view

	def beneficiary() -> address: view

	def future_beneficiary() -> address: view

event FeeGovernorUpdated:
	oldGovernor: indexed(address)
	newGovernor: indexed(address)

fee_governor_address: public(address)
current_fee_governor: FeeGovernor
admin: address

@external
def __init__(_fee_governor_address: address):
	self.fee_governor_address = _fee_governor_address
	self.admin = msg.sender
	self.current_fee_governor = FeeGovernor(_fee_governor_address)

@external
def set_fee_governor(_address: address):
	"""
	@notice Set the payment token governor address for FDT contracts
	@param _address Address of the payment token governer
	"""
	# Check that caller is admin
	assert msg.sender == self.admin
	_previous_fee_governor__address: address = self.fee_governor_address

	self.fee_governor_address = _address
	self.current_fee_governor = FeeGovernor(_address)

	log FeeGovernorUpdated(_previous_fee_governor__address, _address)

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
