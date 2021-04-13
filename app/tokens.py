from concurrent import futures
from typing import Optional, Sequence

from web3.types import BlockData, TxData

from app.crud import Crud
from app.web3_client import Web3Client


def query_ERC20_tokens(*, w3: Web3Client, crud: Crud) -> None:
    block = _get_first_block(w3, crud)
    crud.set_is_block_fetch(True)
    last_block_hash = crud.get_last_block_hash()
    while block and block["hash"] != last_block_hash:
        crud.set_current_block(block["hash"])
        transactions: Sequence[TxData] = block["transactions"]  # type: ignore
        _find_contract_creations(w3, crud, transactions)
        block = w3.get_parent_block(block, full_transactions=True)

    _finish_process(crud)


def _get_first_block(w3: Web3Client, crud: Crud) -> Optional[BlockData]:
    start_block_hash = crud.get_start_block_hash()
    if not start_block_hash:
        block = w3.get_latest_block(full_transactions=True)
        crud.set_start_block(block["hash"])
        return block
    else:
        current_block_hash = crud.get_current_block_hash()
        assert current_block_hash is not None
        return w3.get_block_by_hash(current_block_hash, full_transactions=True)


def _finish_process(crud: Crud) -> None:
    crud.set_last_block(crud.get_start_block_hash())
    crud.set_current_block(None)
    crud.set_start_block(None)
    crud.set_is_block_fetch(False)


def _find_contract_creations_with_threads(
    w3: Web3Client, crud: Crud, transactions: Sequence[TxData]
) -> None:
    if len(transactions) < 1:
        return
    workers = len(transactions)
    with futures.ThreadPoolExecutor(workers) as executor:
        args = ((w3, crud, t) for t in transactions)
        _ = executor.map(lambda p: _save_if_erc20_token(*p), args)


def _find_contract_creations(
    w3: Web3Client, crud: Crud, transactions: Sequence[TxData]
) -> None:
    for t in transactions:
        _save_if_erc20_token(w3, crud, t)


def _save_if_erc20_token(w3: Web3Client, crud: Crud, transaction: TxData) -> None:
    if not w3.is_transaction_contract_creation(transaction):
        return
    address = w3.get_contract_address_by_transaction_hash(transaction["hash"])
    if w3.is_contract_erc20(address):
        crud.save_token_address(address)
