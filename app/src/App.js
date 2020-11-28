import logo from './logo.svg';
import './App.css';

import { FDT_Abi } from './abis';
import React, { useState } from 'react';
import Web3 from 'web3';

const web3 = new Web3(Web3.givenProvider);
const contractAddr = ''
const tokenContract = new web3.eth.Contract(FDT_Abi, contractAddr);

function App() {

  const [getCurrentWallet, setGetCurrentWallet] = useState('0x00');
  const [getTotalSupply, setGetTotalSupply] = useState('0');

  const handleGetCurrentWallet = async (e) => {
    e.preventDefault();
    const accounts = await window.ethereum.enable();
    const account = accounts[0];
    setGetCurrentWallet(account);
    console.log(account);
  }

  const handleGetTotalSupply = async (e) => {
    e.preventDefault();
    const result = web3.utils.fromWei(await tokenContract.methods.totalSupply().call());
    setGetTotalSupply(result);
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


      </header>
    </div>
  );
}

export default App;
