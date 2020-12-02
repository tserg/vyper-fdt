# @version ^0.2.0

# @dev Implementation of ERC-20 token standard.
# @author Takayuki Jimba (@yudetamago)
# https://github.com/ethereum/EIPs/blob/master/EIPS/eip-20.md

from vyper.interfaces import ERC20

implements: ERC20

event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    value: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    value: uint256

event FundsDistributed:
    receiver: indexed(address)
    value: uint256

event FundsWithdrawn:
    receiver: indexed(address)
    value: uint256

name: public(String[64])
symbol: public(String[32])
decimals: public(uint256)

pointsPerShare: uint256

# NOTE: By declaring `balanceOf` as public, vyper automatically generates a 'balanceOf()' getter
#       method to allow access to account balances.
#       The _KeyType will become a required parameter for the getter and it will return _ValueType.
#       See: https://vyper.readthedocs.io/en/v0.1.0-beta.8/types.html?highlight=getter#mappings
balanceOf: public(HashMap[address, uint256])
withdrawnFunds: public(HashMap[address, uint256])
pointsCorrection: public(HashMap[address, int128])
allowances: HashMap[address, HashMap[address, uint256]]
total_supply: uint256
minter: address

fundsBalance: uint256



# ERC20 functions

@external
def __init__(_name: String[64], _symbol: String[32], _decimals: uint256, _supply: uint256):
    self.name = _name
    self.symbol = _symbol
    self.decimals = _decimals
    self.balanceOf[msg.sender] = _supply
    self.total_supply = _supply
    self.minter = msg.sender
    self.fundsBalance = 0
    log Transfer(ZERO_ADDRESS, msg.sender, _supply)


@view
@external
def totalSupply() -> uint256:
    """
    @dev Total number of tokens in existence.
    """
    return self.total_supply


@view
@external
def allowance(_owner : address, _spender : address) -> uint256:
    """
    @dev Function to check the amount of tokens that an owner allowed to a spender.
    @param _owner The address which owns the funds.
    @param _spender The address which will spend the funds.
    @return An uint256 specifying the amount of tokens still available for the spender.
    """
    return self.allowances[_owner][_spender]


@external
def transfer(_to : address, _value : uint256) -> bool:
    """
    @dev Transfer token for a specified address
    @param _to The address to transfer to.
    @param _value The amount to be transferred.
    """
    # NOTE: vyper does not allow underflows
    #       so the following subtraction would revert on insufficient balance
    self.balanceOf[msg.sender] -= _value
    self.balanceOf[_to] += _value
    log Transfer(msg.sender, _to, _value)

    _correction: uint256 = self.pointsPerShare * _value
    self.pointsCorrection[msg.sender] = self.pointsCorrection[msg.sender] + convert(_correction, int128)
    self.pointsCorrection[_to] = self.pointsCorrection[_to] - convert(_correction, int128)

    return True


@external
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    """
     @dev Transfer tokens from one address to another.
     @param _from address The address which you want to send tokens from
     @param _to address The address which you want to transfer to
     @param _value uint256 the amount of tokens to be transferred
    """
    # NOTE: vyper does not allow underflows
    #       so the following subtraction would revert on insufficient balance
    self.balanceOf[_from] -= _value
    self.balanceOf[_to] += _value
    # NOTE: vyper does not allow underflows
    #      so the following subtraction would revert on insufficient allowance
    self.allowances[_from][msg.sender] -= _value
    log Transfer(_from, _to, _value)
    return True


@external
def approve(_spender : address, _value : uint256) -> bool:
    """
    @dev Approve the passed address to spend the specified amount of tokens on behalf of msg.sender.
         Beware that changing an allowance with this method brings the risk that someone may use both the old
         and the new allowance by unfortunate transaction ordering. One possible solution to mitigate this
         race condition is to first reduce the spender's allowance to 0 and set the desired value afterwards:
         https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
    @param _spender The address which will spend the funds.
    @param _value The amount of tokens to be spent.
    """
    self.allowances[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True


@external
def mint(_to: address, _value: uint256):
    """
    @dev Mint an amount of the token and assigns it to an account.
         This encapsulates the modification of balances such that the
         proper events are emitted.
    @param _to The account that will receive the created tokens.
    @param _value The amount that will be created.
    """
    assert msg.sender == self.minter
    assert _to != ZERO_ADDRESS
    self.total_supply += _value
    self.balanceOf[_to] += _value
    log Transfer(ZERO_ADDRESS, _to, _value)


@internal
def _burn(_to: address, _value: uint256):
    """
    @dev Internal function that burns an amount of the token of a given
         account.
    @param _to The account whose tokens will be burned.
    @param _value The amount that will be burned.
    """
    assert _to != ZERO_ADDRESS
    self.total_supply -= _value
    self.balanceOf[_to] -= _value
    log Transfer(_to, ZERO_ADDRESS, _value)


@external
def burn(_value: uint256):
    """
    @dev Burn an amount of the token of msg.sender.
    @param _value The amount that will be burned.
    """
    self._burn(msg.sender, _value)


@external
def burnFrom(_to: address, _value: uint256):
    """
    @dev Burn an amount of the token from a given account.
    @param _to The account whose tokens will be burned.
    @param _value The amount that will be burned.
    """
    self.allowances[_to][msg.sender] -= _value
    self._burn(_to, _value)

# FDT functions

@internal
def accumulativeFundsOf(_receiver: address) -> int128:
    return convert((self.pointsPerShare * self.balanceOf[_receiver]), int128) + self.pointsCorrection[_receiver]

@internal
def withdrawableFundsOf(_receiver: address) -> uint256:
    return convert(self.accumulativeFundsOf(_receiver), uint256) - self.withdrawnFunds[_receiver]

@internal
def _distributeFunds(_triggerer: address, _value: uint256):
    """
    @dev Distribute funds which have not been distributed
    @param _value The amount that will be distributed
    """
    assert self.total_supply > 0

    if _value > 0:
        self.pointsPerShare += _value / self.total_supply

        log FundsDistributed(_triggerer, _value)

@internal
def _updateFundsBalance() -> uint256:
    
    _prevFundsBalance: uint256 = self.fundsBalance

    self.fundsBalance = self.balance

    if _prevFundsBalance > self.fundsBalance:
        return _prevFundsBalance - self.fundsBalance
    elif self.fundsBalance > _prevFundsBalance:
        return self.fundsBalance - _prevFundsBalance
    else:
        return 0


@internal
def _prepareWithdraw(_receiver: address) -> uint256:
    
    _withdrawableDividend: uint256 = self.withdrawableFundsOf(_receiver)

    self.withdrawnFunds[_receiver] = self.withdrawnFunds[_receiver] + _withdrawableDividend

    log FundsWithdrawn(_receiver, _withdrawableDividend)

    return _withdrawableDividend

@external
def withdrawFunds():

    _newFunds: uint256 = self._updateFundsBalance()

    if _newFunds > 0:
        self._distributeFunds(msg.sender, _newFunds)

    _withdrawableFunds: uint256 = self._prepareWithdraw(msg.sender)

    self.fundsBalance -= _withdrawableFunds

    send(msg.sender, _withdrawableFunds)

@view
@external
def withdrawnFundsOf(_receiver: address) -> uint256:
    return self.withdrawnFunds[_receiver]

@external
@payable
def payToContract():
    
    pass

@external
@view
def getPointsPerShare() -> uint256:
    return self.pointsPerShare


@external
@view
def getContractBalance() -> uint256:
    return self.balance