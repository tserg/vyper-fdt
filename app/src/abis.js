export const FDT_Abi = [
  {
	"anonymous": false,
	"inputs": [
	  {
		"indexed": true,
		"name": "sender",
		"type": "address"
	  },
	  {
		"indexed": true,
		"name": "receiver",
		"type": "address"
	  },
	  {
		"indexed": false,
		"name": "value",
		"type": "uint256"
	  }
	],
	"name": "Transfer",
	"type": "event"
  },
  {
	"anonymous": false,
	"inputs": [
	  {
		"indexed": true,
		"name": "owner",
		"type": "address"
	  },
	  {
		"indexed": true,
		"name": "spender",
		"type": "address"
	  },
	  {
		"indexed": false,
		"name": "value",
		"type": "uint256"
	  }
	],
	"name": "Approval",
	"type": "event"
  },
  {
	"anonymous": false,
	"inputs": [
	  {
		"indexed": true,
		"name": "sender",
		"type": "address"
	  },
	  {
		"indexed": false,
		"name": "value",
		"type": "uint256"
	  }
	],
	"name": "FundsDeposited",
	"type": "event"
  },
  {
	"anonymous": false,
	"inputs": [
	  {
		"indexed": true,
		"name": "receiver",
		"type": "address"
	  },
	  {
		"indexed": false,
		"name": "value",
		"type": "uint256"
	  }
	],
	"name": "FundsDistributed",
	"type": "event"
  },
  {
	"anonymous": false,
	"inputs": [
	  {
		"indexed": true,
		"name": "receiver",
		"type": "address"
	  },
	  {
		"indexed": false,
		"name": "value",
		"type": "uint256"
	  }
	],
	"name": "FundsWithdrawn",
	"type": "event"
  },
  {
	"inputs": [],
	"outputs": [],
	"stateMutability": "nonpayable",
	"type": "constructor"
  },
  {
	"gas": 380160,
	"inputs": [
	  {
		"name": "_name",
		"type": "string"
	  },
	  {
		"name": "_symbol",
		"type": "string"
	  },
	  {
		"name": "_decimals",
		"type": "uint256"
	  },
	  {
		"name": "_supply",
		"type": "uint256"
	  },
	  {
		"name": "_ownerAddress",
		"type": "address"
	  }
	],
	"name": "initialize",
	"outputs": [
	  {
		"name": "",
		"type": "bool"
	  }
	],
	"stateMutability": "nonpayable",
	"type": "function"
  },
  {
	"gas": 1208,
	"inputs": [],
	"name": "totalSupply",
	"outputs": [
	  {
		"name": "",
		"type": "uint256"
	  }
	],
	"stateMutability": "view",
	"type": "function"
  },
  {
	"gas": 1668,
	"inputs": [
	  {
		"name": "_owner",
		"type": "address"
	  },
	  {
		"name": "_spender",
		"type": "address"
	  }
	],
	"name": "allowance",
	"outputs": [
	  {
		"name": "",
		"type": "uint256"
	  }
	],
	"stateMutability": "view",
	"type": "function"
  },
  {
	"gas": 148546,
	"inputs": [
	  {
		"name": "_to",
		"type": "address"
	  },
	  {
		"name": "_value",
		"type": "uint256"
	  }
	],
	"name": "transfer",
	"outputs": [
	  {
		"name": "",
		"type": "bool"
	  }
	],
	"stateMutability": "nonpayable",
	"type": "function"
  },
  {
	"gas": 111245,
	"inputs": [
	  {
		"name": "_from",
		"type": "address"
	  },
	  {
		"name": "_to",
		"type": "address"
	  },
	  {
		"name": "_value",
		"type": "uint256"
	  }
	],
	"name": "transferFrom",
	"outputs": [
	  {
		"name": "",
		"type": "bool"
	  }
	],
	"stateMutability": "nonpayable",
	"type": "function"
  },
  {
	"gas": 37971,
	"inputs": [
	  {
		"name": "_spender",
		"type": "address"
	  },
	  {
		"name": "_value",
		"type": "uint256"
	  }
	],
	"name": "approve",
	"outputs": [
	  {
		"name": "",
		"type": "bool"
	  }
	],
	"stateMutability": "nonpayable",
	"type": "function"
  },
  {
	"gas": 75508,
	"inputs": [
	  {
		"name": "_value",
		"type": "uint256"
	  }
	],
	"name": "burn",
	"outputs": [],
	"stateMutability": "nonpayable",
	"type": "function"
  },
  {
	"gas": 111859,
	"inputs": [
	  {
		"name": "_to",
		"type": "address"
	  },
	  {
		"name": "_value",
		"type": "uint256"
	  }
	],
	"name": "burnFrom",
	"outputs": [],
	"stateMutability": "nonpayable",
	"type": "function"
  },
  {
	"gas": 193156,
	"inputs": [],
	"name": "withdrawFunds",
	"outputs": [],
	"stateMutability": "nonpayable",
	"type": "function"
  },
  {
	"gas": 1663,
	"inputs": [
	  {
		"name": "_receiver",
		"type": "address"
	  }
	],
	"name": "withdrawnFundsOf",
	"outputs": [
	  {
		"name": "",
		"type": "uint256"
	  }
	],
	"stateMutability": "view",
	"type": "function"
  },
  {
	"stateMutability": "payable",
	"type": "fallback"
  },
  {
	"gas": 1478,
	"inputs": [],
	"name": "getPointsPerShare",
	"outputs": [
	  {
		"name": "",
		"type": "uint256"
	  }
	],
	"stateMutability": "view",
	"type": "function"
  },
  {
	"gas": 7910,
	"inputs": [],
	"name": "name",
	"outputs": [
	  {
		"name": "",
		"type": "string"
	  }
	],
	"stateMutability": "view",
	"type": "function"
  },
  {
	"gas": 6963,
	"inputs": [],
	"name": "symbol",
	"outputs": [
	  {
		"name": "",
		"type": "string"
	  }
	],
	"stateMutability": "view",
	"type": "function"
  },
  {
	"gas": 1568,
	"inputs": [],
	"name": "decimals",
	"outputs": [
	  {
		"name": "",
		"type": "uint256"
	  }
	],
	"stateMutability": "view",
	"type": "function"
  },
  {
	"gas": 1813,
	"inputs": [
	  {
		"name": "arg0",
		"type": "address"
	  }
	],
	"name": "balanceOf",
	"outputs": [
	  {
		"name": "",
		"type": "uint256"
	  }
	],
	"stateMutability": "view",
	"type": "function"
  }
]

export const FDT_Factory_Abi = [
  {
	"anonymous": false,
	"inputs": [
	  {
		"indexed": false,
		"name": "token",
		"type": "address"
	  },
	  {
		"indexed": false,
		"name": "name",
		"type": "string"
	  },
	  {
		"indexed": false,
		"name": "symbol",
		"type": "string"
	  }
	],
	"name": "FundsDistributionTokenCreated",
	"type": "event"
  },
  {
	"inputs": [
	  {
		"name": "_target",
		"type": "address"
	  },
	  {
		"name": "_admin",
		"type": "address"
	  }
	],
	"outputs": [],
	"stateMutability": "nonpayable",
	"type": "constructor"
  },
  {
	"gas": 60120,
	"inputs": [
	  {
		"name": "_name",
		"type": "string"
	  },
	  {
		"name": "_symbol",
		"type": "string"
	  },
	  {
		"name": "_decimals",
		"type": "uint256"
	  },
	  {
		"name": "_supply",
		"type": "uint256"
	  }
	],
	"name": "deploy_fdt_contract",
	"outputs": [
	  {
		"name": "",
		"type": "address"
	  }
	],
	"stateMutability": "nonpayable",
	"type": "function"
  },
  {
	"gas": 1118,
	"inputs": [],
	"name": "admin",
	"outputs": [
	  {
		"name": "",
		"type": "address"
	  }
	],
	"stateMutability": "view",
	"type": "function"
  },
  {
	"gas": 1148,
	"inputs": [],
	"name": "target",
	"outputs": [
	  {
		"name": "",
		"type": "address"
	  }
	],
	"stateMutability": "view",
	"type": "function"
  }
]
