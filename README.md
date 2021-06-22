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

#### eth-brownie

This project uses eth-brownie for deployment and testing the Vyper smart contracts. The installation instructions can be found in the [documentation](https://eth-brownie.readthedocs.io/en/stable/install.html).

### Local Development

1. To compile the contracts, run:
```
brownie compile
```
2. To deploy the contracts, run:
```
brownie run deploy.py --network development
brownie run deploy_erc20.py --network development
```
3. To deploy to testnets, replace `development` with the applicable name.

### Testing

Run `brownie test`

## Authors

Gary Tse
