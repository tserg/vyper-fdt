export const FDT_Abi = [
    {
      "name": "Transfer",
      "inputs": [
        {
          "type": "address",
          "name": "sender",
          "indexed": true
        },
        {
          "type": "address",
          "name": "receiver",
          "indexed": true
        },
        {
          "type": "uint256",
          "name": "value",
          "indexed": false
        }
      ],
      "anonymous": false,
      "type": "event"
    },
    {
      "name": "Approval",
      "inputs": [
        {
          "type": "address",
          "name": "owner",
          "indexed": true
        },
        {
          "type": "address",
          "name": "spender",
          "indexed": true
        },
        {
          "type": "uint256",
          "name": "value",
          "indexed": false
        }
      ],
      "anonymous": false,
      "type": "event"
    },
    {
      "name": "FundsDistributed",
      "inputs": [
        {
          "type": "address",
          "name": "receiver",
          "indexed": true
        },
        {
          "type": "uint256",
          "name": "value",
          "indexed": false
        }
      ],
      "anonymous": false,
      "type": "event"
    },
    {
      "name": "FundsWithdrawn",
      "inputs": [
        {
          "type": "address",
          "name": "receiver",
          "indexed": true
        },
        {
          "type": "uint256",
          "name": "value",
          "indexed": false
        }
      ],
      "anonymous": false,
      "type": "event"
    },
    {
      "outputs": [],
      "inputs": [
        {
          "type": "string",
          "name": "_name"
        },
        {
          "type": "string",
          "name": "_symbol"
        },
        {
          "type": "uint256",
          "name": "_decimals"
        },
        {
          "type": "uint256",
          "name": "_supply"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "name": "totalSupply",
      "outputs": [
        {
          "type": "uint256",
          "name": ""
        }
      ],
      "inputs": [],
      "stateMutability": "view",
      "type": "function",
      "gas": 1151
    },
    {
      "name": "allowance",
      "outputs": [
        {
          "type": "uint256",
          "name": ""
        }
      ],
      "inputs": [
        {
          "type": "address",
          "name": "_owner"
        },
        {
          "type": "address",
          "name": "_spender"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "gas": 1611
    },
    {
      "name": "transfer",
      "outputs": [
        {
          "type": "bool",
          "name": ""
        }
      ],
      "inputs": [
        {
          "type": "address",
          "name": "_to"
        },
        {
          "type": "uint256",
          "name": "_value"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function",
      "gas": 74833
    },
    {
      "name": "transferFrom",
      "outputs": [
        {
          "type": "bool",
          "name": ""
        }
      ],
      "inputs": [
        {
          "type": "address",
          "name": "_from"
        },
        {
          "type": "address",
          "name": "_to"
        },
        {
          "type": "uint256",
          "name": "_value"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function",
      "gas": 111188
    },
    {
      "name": "approve",
      "outputs": [
        {
          "type": "bool",
          "name": ""
        }
      ],
      "inputs": [
        {
          "type": "address",
          "name": "_spender"
        },
        {
          "type": "uint256",
          "name": "_value"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function",
      "gas": 37914
    },
    {
      "name": "mint",
      "outputs": [],
      "inputs": [
        {
          "type": "address",
          "name": "_to"
        },
        {
          "type": "uint256",
          "name": "_value"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function",
      "gas": 75764
    },
    {
      "name": "burn",
      "outputs": [],
      "inputs": [
        {
          "type": "uint256",
          "name": "_value"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function",
      "gas": 75533
    },
    {
      "name": "burnFrom",
      "outputs": [],
      "inputs": [
        {
          "type": "address",
          "name": "_to"
        },
        {
          "type": "uint256",
          "name": "_value"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function",
      "gas": 111884
    },
    {
      "name": "withdrawFunds",
      "outputs": [],
      "inputs": [],
      "stateMutability": "nonpayable",
      "type": "function",
      "gas": 93105
    },
    {
      "name": "withdrawnFundsOf",
      "outputs": [
        {
          "type": "uint256",
          "name": ""
        }
      ],
      "inputs": [
        {
          "type": "address",
          "name": "_receiver"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "gas": 1786
    },
    {
      "name": "payToContract",
      "outputs": [],
      "inputs": [],
      "stateMutability": "payable",
      "type": "function",
      "gas": 41063
    },
    {
      "name": "getPointsPerShare",
      "outputs": [
        {
          "type": "uint256",
          "name": ""
        }
      ],
      "inputs": [],
      "stateMutability": "view",
      "type": "function",
      "gas": 1631
    },
    {
      "name": "getContractBalance",
      "outputs": [
        {
          "type": "uint256",
          "name": ""
        }
      ],
      "inputs": [],
      "stateMutability": "view",
      "type": "function",
      "gas": 863
    },
    {
      "name": "name",
      "outputs": [
        {
          "type": "string",
          "name": ""
        }
      ],
      "inputs": [],
      "stateMutability": "view",
      "type": "function",
      "gas": 8093
    },
    {
      "name": "symbol",
      "outputs": [
        {
          "type": "string",
          "name": ""
        }
      ],
      "inputs": [],
      "stateMutability": "view",
      "type": "function",
      "gas": 7146
    },
    {
      "name": "decimals",
      "outputs": [
        {
          "type": "uint256",
          "name": ""
        }
      ],
      "inputs": [],
      "stateMutability": "view",
      "type": "function",
      "gas": 1751
    },
    {
      "name": "balanceOf",
      "outputs": [
        {
          "type": "uint256",
          "name": ""
        }
      ],
      "inputs": [
        {
          "type": "address",
          "name": "arg0"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "gas": 1996
    }
  ]