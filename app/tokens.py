import logging
import time
from concurrent import futures
from typing import Optional, Sequence

from eth_tester.exceptions import TransactionFailed
from hexbytes import HexBytes
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput, InvalidAddress
from web3.types import BlockData, ChecksumAddress

from app.crud import Crud

logging.getLogger().setLevel(logging.INFO)


ERC20_ABI_VIEWS = [
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [{"name": "who", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"name": "remaining", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]


def query_ERC20_tokens(*, w3: Web3, crud: Crud) -> None:
    logging.info("getting starting block")
    block = _get_starting_block(w3, crud)
    while block:
        logging.info(f"block hash: {block['hash'].hex()}")
        transactions: Sequence[HexBytes] = block["transactions"]  # type: ignore
        logging.info(f"number of transactions to parse: {len(transactions)}")
        _find_contract_creations(transactions)
        logging.info("done parsing transactions")
        crud.save_as_earliest_block(block["hash"])
        block = _get_parent_block(w3, block)
    logging.info("done")


def _get_starting_block(w3: Web3, crud: Crud) -> Optional[BlockData]:
    earliest_queried_block_address = crud.get_earliest_block_address()
    if not earliest_queried_block_address:
        logging.info("there's no earliest block in db, getting 'latest'")
        block = w3.eth.get_block("latest")
        crud.save_as_last_block(block["hash"])
        return block
    else:
        logging.info(f"earliest block: {earliest_queried_block_address.hex()}")
        earliest_block = w3.eth.get_block(earliest_queried_block_address)
        logging.info("getting parent")
        return _get_parent_block(w3, earliest_block)


def _get_parent_block(w3: Web3, block: BlockData) -> Optional[BlockData]:
    ZERO_HASH = "0x0000000000000000000000000000000000000000000000000000000000000000"
    parent_hash = block["parentHash"]
    if parent_hash.hex() == ZERO_HASH:
        return None
    return w3.eth.get_block(parent_hash)


def _find_contract_creations(transactions: Sequence[HexBytes]) -> None:
    if len(transactions) < 1:
        return

    start = time.time()
    workers = len(transactions)
    with futures.ThreadPoolExecutor(workers) as executor:
        _ = executor.map(_save_if_erc20_token, transactions)
    end = time.time()
    logging.info(f"time: {end - start}")


def _save_if_erc20_token(w3: Web3, crud: Crud, transaction_hash: HexBytes) -> None:
    if not _is_contract_creation(w3, transaction_hash):
        return
    address = _get_contract_address(w3, transaction_hash)
    if is_contract_erc20_complient(w3, address):
        crud.save_token_address(address)


def _is_contract_creation(w3, transaction_hash: HexBytes) -> bool:
    return w3.eth.get_transaction(transaction_hash).get("to") is None


def _get_contract_address(w3, transaction_hash: HexBytes) -> ChecksumAddress:
    return w3.eth.getTransactionReceipt(transaction_hash)["contractAddress"]


def is_contract_erc20_complient(w3: Web3, contract_address: ChecksumAddress) -> bool:
    try:
        contract = w3.eth.contract(address=contract_address, abi=ERC20_ABI_VIEWS)
    except (InvalidAddress, BadFunctionCallOutput):
        return False
    try:
        test_addr = contract_address
        contract.functions.totalSupply().call()
        contract.functions.balanceOf(test_addr).call()
        contract.functions.allowance(test_addr, test_addr).call()
    except (TransactionFailed, BadFunctionCallOutput):
        return False
    return True
