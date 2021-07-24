# @version ^0.2.0

# @dev Fee governor for Funds Distribution Token
# @author Gary Tse (@tserg)

event newAdminFeeCommitted:
	new_admin_fee: uint256

event newAdminFeeApplied:
	new_admin_fee: uint256

event newBeneficiaryCommitted:
	beneficiary: address

event newBeneficiaryApplied:
	beneficiary: address

ADMIN_ACTIONS_DELAY: constant(uint256) = 3 * 86400

# @dev Address of admin of contract
admin: address

# @dev Current admin fee
admin_fee: public(uint256)

# @dev Future admin fee
future_admin_fee: public(uint256)

# @dev Deadline for change of admin fee
admin_fee_action_deadline: uint256

# @dev Address of beneficiary to send admin fees to
beneficiary: public(address)

# @dev New address of beneficiary
future_beneficiary: public(address)

# @dev Deadline for change of admin fee
admin_beneficiary_action_deadline: uint256



@external
def __init__(_admin_fee: uint256):
	"""
	@notice Contract constructor
	@param _admin_fee Admin fee
	"""
	self.admin = msg.sender
	self.admin_fee = _admin_fee
	self.beneficiary = msg.sender

@external
def commit_new_admin_fee(_new_admin_fee: uint256):
	"""
	@notice Change admin fee
	@param _new_admin_fee New admin fee
	"""
	assert msg.sender == self.admin
	assert self.admin_fee_action_deadline == 0
	assert _new_admin_fee != self.admin_fee

	deadline: uint256 = block.timestamp + ADMIN_ACTIONS_DELAY
	self.admin_fee_action_deadline = deadline
	self.future_admin_fee = _new_admin_fee

	log newAdminFeeCommitted(_new_admin_fee)

@external
def apply_new_admin_fee():
	"""
	@notice Apply new admin fee
	"""
	assert msg.sender == self.admin
	assert block.timestamp >= self.admin_fee_action_deadline

	self.admin_fee_action_deadline = 0
	admin_fee: uint256 = self.future_admin_fee
	self.admin_fee = admin_fee

	log newAdminFeeApplied(self.admin_fee)

@external
def commit_new_beneficiary(_new_beneficiary: address):
	"""
	@notice Change beneficiary address for admin fee
	@param _new_beneficiary Address to send admin fee to
	"""
	assert msg.sender == self.admin
	assert self.admin_beneficiary_action_deadline == 0
	assert _new_beneficiary != ZERO_ADDRESS, "Beneficiary address cannot be zero address"
	assert _new_beneficiary != self.beneficiary, "Beneficiary address cannot be existing beneficiary address"

	deadline: uint256 = block.timestamp + ADMIN_ACTIONS_DELAY
	self.admin_beneficiary_action_deadline = deadline
	self.future_beneficiary = _new_beneficiary

	log newBeneficiaryCommitted(_new_beneficiary)


@external
def apply_new_beneficiary():
	"""
	@notice Apply new beneficiary
	"""
	assert msg.sender == self.admin
	assert block.timestamp >= self.admin_beneficiary_action_deadline

	self.admin_beneficiary_action_deadline = 0
	beneficiary: address = self.future_beneficiary
	self.beneficiary = beneficiary

	log newBeneficiaryApplied(self.beneficiary)
