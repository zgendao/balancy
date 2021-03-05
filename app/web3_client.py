from typing import Tuple

from web3 import Web3

from app.config import config

w3 = Web3(Web3.HTTPProvider(config.WEB3_PROVIDER))


def get_eth_balance(account: str) -> float:
    wei = w3.eth.getBalance(account)
    return w3.fromWei(wei, "ether")


def get_accounts() -> Tuple[str]:
    return w3.eth.accounts
