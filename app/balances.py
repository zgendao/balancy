import datetime
from typing import Dict

from web3 import Web3

from app.crud import Crud

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


def fetch_address_token_balances(address: str, *, w3: Web3, crud: Crud) -> Dict:
    session_obj = {
        "address": address,
        "started_at": datetime.datetime.utcnow().timestamp(),
        "processing": True,
    }
    crud.save_address_balances(address, session_obj)

    token_addresses = crud.get_token_addresses()
    for token_addr in token_addresses:
        balance = balance_of_address(address, token_addr, w3=w3)
        session_obj.update({token_addr: balance})
        crud.save_address_balances(address, session_obj)

    session_obj["processing"] = False
    crud.save_address_balances(address, session_obj)
    return session_obj


def balance_of_address(address: str, token_address: str, *, w3: Web3) -> int:
    try:
        cs_address = w3.toChecksumAddress(address)
        token_cs_address = w3.toChecksumAddress(token_address)
    except ValueError:
        return 0
    contract = w3.eth.contract(address=token_cs_address, abi=ABI_FOR_BALANCE_OF)
    res = contract.functions.balanceOf(cs_address).call()
    return res
