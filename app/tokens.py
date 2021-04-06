from concurrent import futures
from typing import Optional, Sequence

from hexbytes import HexBytes
from web3.types import BlockData

from app.crud import Crud
from app.web3_client import Web3Client


def query_ERC20_tokens(*, w3: Web3Client, crud: Crud) -> None:
    block = _get_first_block(w3, crud)
    crud.set_is_block_fetch(True)
    last_block_hash = crud.get_last_block_hash()
    while block and block["hash"] != last_block_hash:
        crud.set_current_block(block["hash"])
        transactions: Sequence[HexBytes] = block["transactions"]  # type: ignore
        _find_contract_creations(transactions)
        block = w3.get_parent_block(block)
    _finish_process(crud)


def _get_first_block(w3: Web3Client, crud: Crud) -> Optional[BlockData]:
    start_block_hash = crud.get_start_block_hash()
    if not start_block_hash:
        block = w3.get_latest_block()
        crud.set_start_block(block["hash"])
        return block
    else:
        current_block_hash = crud.get_current_block_hash()
        assert current_block_hash is not None
        return w3.get_block_by_hash(current_block_hash)


def _finish_process(crud: Crud) -> None:
    crud.set_last_block(crud.get_start_block_hash())
    crud.set_current_block(None)
    crud.set_start_block(None)
    crud.set_is_block_fetch(False)


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
