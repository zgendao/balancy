from typing import Optional, Tuple
from urllib.parse import urlparse

from web3 import Web3

from app.config import config


class Web3Client:
    def __init__(self, web3_provider_url: Optional[str] = None):
        if not web3_provider_url:
            url = config.WEB3_PROVIDER
        else:
            url = web3_provider_url
        self.w3 = Web3(Web3.HTTPProvider(url))

    def get_eth_balance(self, account: str) -> float:
        wei = self.w3.eth.getBalance(account)
        return self.w3.fromWei(wei, "ether")

    def get_accounts(self) -> Tuple[str]:
        return self.w3.eth.accounts


def get_w3(web3_provider_url: Optional[str] = None):
    if not web3_provider_url:
        url = config.WEB3_PROVIDER
    else:
        url = web3_provider_url

    parsed_url = urlparse(url)
    if parsed_url.scheme in ("ws", "wss"):
        return Web3(Web3.WebsocketProvider(url))
    elif parsed_url.scheme in ("http", "https"):
        return Web3(Web3.HTTPProvider(url))
    else:
        raise ValueError("invalid scheme for web3 provider url")
