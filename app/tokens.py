from concurrent import futures
from typing import Optional, Sequence

from hexbytes import HexBytes
from web3.types import BlockData

from app.crud import Crud
from app.web3_client import Web3Client


def query_ERC20_tokens(*, w3: Web3Client, crud: Crud) -> None:
    block = _get_starting_block(w3, crud)
    while block:
        transactions: Sequence[HexBytes] = block["transactions"]  # type: ignore
        _find_contract_creations(transactions)
        crud.save_as_earliest_block(block["hash"])
        block = w3.get_parent_block(block)


def _get_starting_block(w3: Web3Client, crud: Crud) -> Optional[BlockData]:
    earliest_queried_block_hash = crud.get_earliest_block_address()
    if not earliest_queried_block_hash:
        block = w3.get_latest_block()
        crud.save_as_last_block(block["hash"])
        return block
    else:
        earliest_block = w3.get_block_by_hash(earliest_queried_block_hash)
        return w3.get_parent_block(earliest_block)


def _find_contract_creations(transactions: Sequence[HexBytes]) -> None:
    if len(transactions) < 1:
        return
    workers = len(transactions)
    with futures.ThreadPoolExecutor(workers) as executor:
        _ = executor.map(_save_if_erc20_token, transactions)


def _save_if_erc20_token(
    w3: Web3Client, crud: Crud, transaction_hash: HexBytes
) -> None:
    if not w3.is_transaction_contract_creation(transaction_hash):
        return
    address = w3.get_contract_address_by_transaction_hash(transaction_hash)
    if w3.is_contract_erc20(address):
        crud.save_token_address(address)
