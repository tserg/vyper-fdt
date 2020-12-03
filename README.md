# Vyper Implementation of Funds Distribution Token

Test Vyper implementation of ERC-2222 with ERC20 tokens as payment/dividends. Code adapted from: https://github.com/atpar/funds-distribution-token/tree/master/contracts/external/math

This is a Funds Distribution Token (FDT) that allows a contract to receive payment in an ERC20 token, and allow its owners to claim a proportion of the payments received by the token contract based on their percentage ownership.

For example, if 100 X tokens were paid, and Alice owns 10 out of 100 FDT, Alice can withdraw (10/100) * 100 = 10 X tokens.

In this implementation, FDT is capped at 100 with 0 decimal places. Each FDT therefore represents 1%.

By minting the FDTs at token creation, we can mint a number of FDTs to a rentseeker's wallet address.

This is a further modification of https://github.com/tserg/funds-distribution-token-custom where the FDT contract is deployed using a factory contract.

## Getting Started

#### Python 3.8

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by running:
```bash
pip install -r requirements.txt
```
This will install all of the required packages we selected within the `requirements.txt` file.

### Local Development

1. Launch your development blockchain in a terminal. Here, we use ganache-cli with port 8545.
```
ganache-cli
```
2. In a separate terminal, navigate to the directory and migrate the contracts to the development blockchain. If your development blockchain is using a different port, please amend `truffle-config.js`.
```
truffle migrate --network development
```
3. Replace line 9 in app/App.js with the deployed contract address.
4. Navigate to the `app` directory and launch the React app.
```
cd app
npm start
```

### Testing

Run `brownie test`

## Authors

Gary Tse