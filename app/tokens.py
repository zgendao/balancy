from typing import Any

from web3 import Web3

from app.crud import Crud


def query_ERC20_tokens(*, w3: Web3, crud: Crud) -> Any:
    ...
