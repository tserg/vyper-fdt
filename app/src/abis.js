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
      "gas": 1151,
      "constant": true
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
      "gas": 1611,
      "constant": true
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
      "gas": 148489
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
      "gas": 193899
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
      "gas": 1816,
      "constant": true
    },
    {
      "name": "payToContract",
      "outputs": [],
      "inputs": [],
      "stateMutability": "payable",
      "type": "function",
      "gas": 696,
      "payable": true
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
      "gas": 1661,
      "constant": true
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
      "gas": 893,
      "constant": true
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
      "gas": 8123,
      "constant": true
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
      "gas": 7176,
      "constant": true
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
      "gas": 1781,
      "constant": true
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
      "gas": 2026,
      "constant": true
    },
    {
      "name": "withdrawnFunds",
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
      "gas": 2056,
      "constant": true
    },
    {
      "name": "pointsCorrection",
      "outputs": [
        {
          "type": "int128",
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
      "gas": 2086,
      "constant": true
    }
  ]