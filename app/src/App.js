import logo from './logo.svg';
import './App.css';

import { FDT_Abi } from './abis';
import React, { useState } from 'react';
import Web3 from 'web3';

const web3 = new Web3(Web3.givenProvider);
const contractAddr = '';
const FDTContract = new web3.eth.Contract(FDT_Abi, contractAddr);

function App() {

  const [getCurrentWallet, setGetCurrentWallet] = useState('0x00');
  const [getTotalSupply, setGetTotalSupply] = useState('0');
  const [getCurrentWalletTokenBalance, setGetCurrentWalletTokenBalance] = useState('0');
  const [getCurrentWalletWithdrawnFunds, setGetCurrentWalletWithdrawnFunds] = useState('0');
  const [getPointsCorrection, setGetPointsCorrection] = useState('0');
  const [payAmount, setPayAmount] = useState(0);
  const [getContractBalance, setGetContractBalance] = useState(0);

  const handleGetCurrentWallet = async (e) => {
    e.preventDefault();
    const accounts = await window.ethereum.enable();
    const account = accounts[0];
    setGetCurrentWallet(account);
    console.log(account);
  }

  const handleGetTotalSupply = async (e) => {
    e.preventDefault();
    const result = await FDTContract.methods.totalSupply().call();
    setGetTotalSupply(result);
    console.log(result);
  }

  const handlePay = async (e) => {
    e.preventDefault();
    const accounts = await window.ethereum.enable();
    const account = accounts[0];
    const payAmountFormatted = web3.utils.toWei(payAmount, 'ether');
    console.log(payAmountFormatted);
    const result = await FDTContract.methods.payToContract().send({from: account, value: payAmountFormatted});
    console.log(result);
  }

  const handleGetContractBalance = async (e) => {
    e.preventDefault();
    const result = web3.utils.fromWei(await FDTContract.methods.getContractBalance().call());
    setGetContractBalance(result);
    console.log(result);
  }

  const handleWithdrawFunds = async (e) => {
    e.preventDefault();
    const accounts = await window.ethereum.enable();
    const account = accounts[0];
    const result = await FDTContract.methods.withdrawFunds().send({from: account});
    console.log(result);
  }

  const handleGetCurrentWalletTokenBalance = async (e) => {
    e.preventDefault();
    const accounts = await window.ethereum.enable();
    const account = accounts[0];
    const result = await FDTContract.methods.balanceOf(account).call();
    setGetCurrentWalletTokenBalance(result);
    console.log(result);

  }

  const handleGetCurrentWalletWithdrawnFunds = async (e) => {
    e.preventDefault();
    const accounts = await window.ethereum.enable();
    const account = accounts[0];
    const result = web3.utils.fromWei(await FDTContract.methods.withdrawnFunds(account).call());
    setGetCurrentWalletWithdrawnFunds(result);
    console.log(result);
  }

  const handleGetPointsCorrection = async (e) => {
    e.preventDefault();
    const accounts = await window.ethereum.enable();
    const account = accounts[0];
    const result = web3.utils.fromWei(await FDTContract.methods.pointsCorrection(account).call());
    setGetPointsCorrection(result);
    console.log(result);
  }

  return (
    <div className="App">
      <header className="App-header">

        <button
          onClick={handleGetCurrentWallet}
          type="button" > 
          Connect Wallet
        </button>
        <p>
          Current Wallet: &nbsp;
          { getCurrentWallet }
        </p>

        <button
          onClick={handleGetTotalSupply}
          type="button" > 
          Get Total Supply
        </button>
        <p>Total Supply: &nbsp;
        { getTotalSupply }
        </p>

        <button
          onClick={handleGetCurrentWalletTokenBalance}
          type="button" > 
          Get Current Wallet Token Balance
        </button>
        <p>Number of tokens in current wallet: &nbsp;
        { getCurrentWalletTokenBalance }
        </p>

        <button
          onClick={handleGetContractBalance}
          type="button" > 
          Get Contract Balance
        </button>
        <p>Contract balance: &nbsp;
        { getContractBalance }
        </p>

        <button
          onClick={handleGetCurrentWalletWithdrawnFunds}
          type="button" > 
          Get Current Wallet Withdrawn Funds
        </button>
        <p>Funds withdrawn: &nbsp;
        { getCurrentWalletWithdrawnFunds }
        </p>

        <button
          onClick={handleGetPointsCorrection}
          type="button" > 
          Get points correction
        </button>
        <p>Points correction: &nbsp;
        { getPointsCorrection }
        </p>

        <form onSubmit={handlePay}>
          <p>
          <label>
            Pay to Contract:
            <input 
              type="text"
              name="name"
              value={payAmount}
              onChange={ e => setPayAmount(e.target.value) } />
          </label>
          <input type="submit" value="Pay" />
          </p>
        </form>

        <button
          onClick={handleWithdrawFunds}
          type="button" >
          Withdraw Funds
        </button>

      </header>
    </div>
  );
}

export default App;
