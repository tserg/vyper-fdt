import logo from './logo.svg';
import './App.css';

import { FDT_Abi, FDT_Factory_Abi } from './abis';
import React, { useState } from 'react';
import Web3 from 'web3';

const web3 = new Web3(Web3.givenProvider);
const contractAddr = '0x2fC132b0576a5fFa478c09998B9b82C47A7D3c2A';
const factoryContractAddr = '0x2146BEe7Ff94d76B5844AFB8262a987e7061C9f6';
const FDTContract = new web3.eth.Contract(FDT_Abi, contractAddr);
const FDTFactoryContract = new web3.eth.Contract(FDT_Factory_Abi, factoryContractAddr)

function App() {

  const [getCurrentWallet, setGetCurrentWallet] = useState('0x00');
  const [getTotalSupply, setGetTotalSupply] = useState('0');
  const [getCurrentWalletTokenBalance, setGetCurrentWalletTokenBalance] = useState('0');
  const [getCurrentWalletWithdrawnFunds, setGetCurrentWalletWithdrawnFunds] = useState('0');
  const [payAmount, setPayAmount] = useState(0);
  const [getContractBalance, setGetContractBalance] = useState(0);
  const [getMusicakesAddress, setMusicakesAddress] = useState('0x');

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
    web3.eth.sendTransaction({from: account, to: contractAddr, value: payAmountFormatted});
  }

  const handleGetContractBalance = async (e) => {
    e.preventDefault();
    const result = web3.utils.fromWei(await web3.eth.getBalance(contractAddr));
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
    const result = web3.utils.fromWei(await FDTContract.methods.withdrawnFundsOf(account).call());
    setGetCurrentWalletWithdrawnFunds(result);
    console.log(result);
  }

  const handleDeployMusicakes = async (e) => {
	  e.preventDefault();
	  const accounts = await window.ethereum.enable();
      const account = accounts[0];
      const result = await FDTFactoryContract.methods.deploy_fdt_contract("Musicakes", "MCAKES", 0, 100).send({from: account});

	  console.log(result);
	  console.log(result.events.FundsDistributionTokenCreated)
	  console.log(result.events.FundsDistributionTokenCreated.returnValues[0])
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
          onClick={handleDeployMusicakes}
          type="button" >
          Deploy Musicakes
        </button>
        <p>
          Musicakes address: &nbsp;
          { getMusicakesAddress }
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
