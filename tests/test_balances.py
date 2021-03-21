import json

from solcx import compile_standard
from web3 import Web3

from app.balances import balance_of_address

w3 = Web3(Web3.EthereumTesterProvider())


SOURCE_CODE_TOKEN = """
    pragma solidity ^0.8.0;

    contract TestToken {
        mapping (address => uint) public balances;

        constructor() public {}

        function mint(address receiver, uint amount) public {
            require(amount < 1e60);
            balances[receiver] += amount;
        }

        function balanceOf(address owner)
        public view returns (uint256) {
            return balances[owner];
        }
    }"""


def create_test_contract():
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"TestToken.sol": {"content": SOURCE_CODE_TOKEN}},
            "settings": {
                "outputSelection": {
                    "*": {"*": ["metadata", "evm.bytecode", "evm.bytecode.sourceMap"]}
                }
            },
        }
    )
    w3.eth.default_account = w3.eth.accounts[0]
    bytecode = compiled_sol["contracts"]["TestToken.sol"]["TestToken"]["evm"][
        "bytecode"
    ]["object"]
    abi = json.loads(
        compiled_sol["contracts"]["TestToken.sol"]["TestToken"]["metadata"]
    )["output"]["abi"]

    TestToken = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = TestToken.constructor().transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    contract_address = tx_receipt["contractAddress"]
    return contract_address, abi


def add_tokens_to_address(contract_address, abi, add_address, amount):
    cont = w3.eth.contract(contract_address, abi=abi)
    tx_hash = cont.functions.mint(add_address, amount).transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_receipt


def setup_test_contract_with_balance(test_address, balance):
    contract_address, abi = create_test_contract()
    add_tokens_to_address(contract_address, abi, test_address, balance)
    return contract_address


def test_balance_of_address():
    test_address = "0x7FcaFF4Ba5E113B6f2c4bC518A161b3d7F1A9AD7"
    expected_amount = 42
    contract_address = setup_test_contract_with_balance(test_address, expected_amount)

    result_amount = balance_of_address(test_address, contract_address, w3=w3)
    assert expected_amount == result_amount


def test_balance_of_address_invalid_address():
    invalid_address = "0x7FcaFF4Ba5E113B6f2c4bC518A161b3d7F1A9AD7asdf"
    result_amount = balance_of_address(invalid_address, invalid_address, w3=w3)
    assert result_amount == 0
