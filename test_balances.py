import json

from eth_tester.exceptions import TransactionFailed
from solcx import compile_standard
from web3 import Web3

erc20_abi = [
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [{"name": "who", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"name": "remaining", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]
# Solidity source code
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {
            "Greeter.sol": {
                "content": """
                pragma solidity ^0.8.0;

                contract Greeter {
                  string public greeting;

                  constructor() public {
                      greeting = 'Hello';
                  }

                  function setGreeting(string memory _greeting) public {
                      greeting = _greeting;
                  }

                  function greet() view public returns (string memory) {
                      return greeting;
                  }
                  function totalSupply() view public returns (uint256) {
                      return 1;
                  }

                  function allowance(address owner, address spender)
                  public view returns (uint256) {
                      return 1;
                  }
                }
              """
            }
        },
        "settings": {
            "outputSelection": {
                "*": {"*": ["metadata", "evm.bytecode", "evm.bytecode.sourceMap"]}
            }
        },
    }
)

w3 = Web3(Web3.EthereumTesterProvider())

w3.eth.default_account = w3.eth.accounts[0]

bytecode = compiled_sol["contracts"]["Greeter.sol"]["Greeter"]["evm"]["bytecode"][
    "object"
]

abi = json.loads(compiled_sol["contracts"]["Greeter.sol"]["Greeter"]["metadata"])[
    "output"
]["abi"]


Greeter = w3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = Greeter.constructor().transact()
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

contract_address = tx_receipt["contractAddress"]
print(type(contract_address))

greeter = w3.eth.contract(address=contract_address, abi=erc20_abi)

try:
    print(greeter.functions.balanceOf(contract_address).call())
except TransactionFailed:
    print("noice")
except Exception as err:
    print(type(err))
    raise err


# tx_hash = greeter.functions.setGreeting("Nihao").transact()
# tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
# print(greeter.functions.greet().call())
