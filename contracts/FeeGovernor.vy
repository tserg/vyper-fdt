# @version ^0.2.0

# @dev Fee governor for Funds Distribution Token
# @author Gary Tse (@tserg)

event newAdminFeeCommitted:
	new_admin_fee: uint256

event newAdminFeeApplied:
	new_admin_fee: uint256

ADMIN_ACTIONS_DELAY: constant(uint256) = 3 * 86400

admin_fee: public(uint256)
future_admin_fee: public(uint256)
admin_action_deadline: uint256
admin: address

# @dev Address of beneficiary to send admin fees to
beneficiary: public(address)

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
	assert _new_admin_fee != self.admin_fee

	deadline: uint256 = block.timestamp + ADMIN_ACTIONS_DELAY
	self.admin_action_deadline = deadline
	self.future_admin_fee = _new_admin_fee

	log newAdminFeeCommitted(_new_admin_fee)

@external
def apply_new_admin_fee():
	assert msg.sender == self.admin
	assert block.timestamp >= self.admin_action_deadline

	self.admin_action_deadline = 0
	admin_fee: uint256 = self.future_admin_fee
	self.admin_fee = admin_fee

	log newAdminFeeApplied(self.admin_fee)
