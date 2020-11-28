import logo from './logo.svg';
import './App.css';

import { FDT_Abi } from './abis';
import React, { useState } from 'react';
import Web3 from 'web3';

const web3 = new Web3(Web3.givenProvider);
const contractAddr = '0xEE97EA62EeDe2e522B967C14d7de0a363f6c9341';
const FDTContract = new web3.eth.Contract(FDT_Abi, contractAddr);

function App() {

  const [getCurrentWallet, setGetCurrentWallet] = useState('0x00');
  const [getTotalSupply, setGetTotalSupply] = useState('0');
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
    const result = web3.utils.fromWei(await FDTContract.methods.totalSupply().call());
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
          onClick={handleGetContractBalance}
          type="button" > 
          Get Contract Balance
        </button>
        <p>Contract balance: &nbsp;
        { getContractBalance }
        </p>

        <form onSubmit={handlePay}>
          <label>
            Pay to Contract:
            <input 
              type="text"
              name="name"
              value={payAmount}
              onChange={ e => setPayAmount(e.target.value) } />
          </label>
          <input type="submit" value="Pay" />
        </form>


      </header>
    </div>
  );
}

export default App;
