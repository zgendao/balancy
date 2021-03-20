from web3 import Web3

ABI_FOR_BALANCE_OF = [
    {
        "constant": True,
        "inputs": [{"name": "who", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]


def balance_of_address(address: str, token_address: str, *, w3: Web3) -> int:
    try:
        cs_address = w3.toChecksumAddress(address)
        token_cs_address = w3.toChecksumAddress(token_address)
    except ValueError:
        return 0
    contract = w3.eth.contract(address=token_cs_address, abi=ABI_FOR_BALANCE_OF)
    res = contract.functions.balanceOf(cs_address).call()
    return res
