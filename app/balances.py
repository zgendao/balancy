from web3 import Web3

from app.crud import Crud


def get_token_balance(address: str, token: str, *, w3: Web3, crud: Crud) -> int:
    ...
