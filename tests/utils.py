import json

from solcx import compile_standard

SOURCE_CODE_ERC20_CONTRACT = """
    pragma solidity ^0.8.0;

    contract TestERC20 {
      string public greeting;

      constructor() public {
          greeting = 'Hello';
      }

      function totalSupply() view public returns (uint256) {
          return 1;
      }

      function balanceOf(address owner)
      public view returns (uint256) {
          return 1;
      }

      function allowance(address owner, address spender)
      public view returns (uint256) {
          return 1;
      }
    }"""

SOURCE_CODE_NOT_ERC20_CONTRACT = """
    pragma solidity ^0.8.0;

    contract TestERC20 {
      string public greeting;

      constructor() public {
          greeting = 'Hello';
      }

      function totalSupply() view public returns (uint256) {
          return 1;
      }

      function allowance(address owner, address spender)
      public view returns (uint256) {
          return 1;
      }
    }"""


def create_contract(w3, source_code):
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"TestERC20.sol": {"content": source_code}},
            "settings": {
                "outputSelection": {
                    "*": {"*": ["metadata", "evm.bytecode", "evm.bytecode.sourceMap"]}
                }
            },
        }
    )
    w3.eth.default_account = w3.eth.accounts[0]
    bytecode = compiled_sol["contracts"]["TestERC20.sol"]["TestERC20"]["evm"][
        "bytecode"
    ]["object"]
    abi = json.loads(
        compiled_sol["contracts"]["TestERC20.sol"]["TestERC20"]["metadata"]
    )["output"]["abi"]

    TestERC20 = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = TestERC20.constructor().transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    contract_address = tx_receipt["contractAddress"]
    return tx_hash, contract_address
