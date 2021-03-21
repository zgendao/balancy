import json

from solcx import compile_standard
from web3 import Web3

from app.tokens import is_contract_erc20_complient

w3 = Web3(Web3.EthereumTesterProvider())


source_code_erc20 = """
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

source_code_missing_balance_of = """
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


def create_contract(source_code):
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
    return contract_address


def test_is_contract_erc20_complient():
    contract_address = create_contract(source_code_erc20)
    assert is_contract_erc20_complient(w3, contract_address)


def test_is_contract_erc20_complient_not_erc20():
    contract_address = create_contract(source_code_missing_balance_of)
    assert not is_contract_erc20_complient(w3, contract_address)


def test_is_contract_erc20_complient_invalid_address():
    invalid_address = "0xB8c77482e45F1F44dE1745F52C74426C631bDD52"
    assert not is_contract_erc20_complient(w3, invalid_address)
