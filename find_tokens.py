import time
from concurrent import futures
from typing import List, Optional

from hexbytes import HexBytes

from app.web3_client import get_w3

w3 = get_w3()

zero_byte = HexBytes(bytearray(1))


def find_contract_creation():
    count = 0
    max_count = 10000
    found_a_contract = False

    block = w3.eth.get_block("latest")
    contract_creations = []

    while count < max_count and not found_a_contract:
        print(f"count: {count} - In block {block['hash'].hex()}")
        transactions = block["transactions"]
        for i, t in enumerate(transactions):
            print(f"transaction {i} in {len(transactions)}")
            if w3.eth.get_transaction(t).get("to") is None:
                print("Found one! Transaction hash:")
                print(t.hex())
                found_a_contract = True
                contract_creations.append(t)
                break
        count += 1
        block = w3.eth.get_block(block["parentHash"])


def _is_contract_creation(num: int, transaction_hash: HexBytes) -> Optional[HexBytes]:
    print(f"{num} start")
    is_contract = w3.eth.get_transaction(transaction_hash).get("to") is None
    if is_contract:
        # print(f"transaction {num}: {transaction_hash.hex()} is contract!!!!!")
        print(f"{num} done")
        res = transaction_hash
    else:
        # print(f"transaction {num}: {transaction_hash.hex()} not a contract")
        res = None
    print(f"{num} done")
    return res


def _get_contract_address(transaction_hash: HexBytes):
    return w3.eth.getTransactionReceipt(transaction_hash)["contractAddress"]


def _query_transactions(transactions: List[HexBytes]) -> List[HexBytes]:
    start = time.time()

    contract_creations = []
    for i, t in enumerate(transactions):
        # print(f"transaction {i} in {len(transactions)}")
        if _is_contract_creation(i, t):
            contract_creations.append(t)

    end = time.time()
    print(end - start)
    return contract_creations


def _query_with_futures(transactions: List[HexBytes]) -> List[HexBytes]:
    start = time.time()

    workers = len(transactions)
    with futures.ThreadPoolExecutor(workers) as executor:
        args = ((i, t) for i, t in enumerate(transactions))
        _ = executor.map(lambda p: _is_contract_creation(*p), args)

    end = time.time()
    print(end - start)
    return []


def _query_with_asyncio(transactions: List[HexBytes]) -> List[HexBytes]:
    start = time.time()
    end = time.time()
    print(end - start)
    return []


test_block = w3.eth.get_block(
    "0x1714c678a71b94d11631a911085e0ecb6b25dd7a4646a9d85a368eb9ebffc3e6"
)
contract_transaction = w3.eth.get_transaction(
    "0xb1874452e2ed691c16419c230cd773cd1a51fd36e5154e9f916c8506e21e3593"
)
test_transactions = test_block["transactions"]

# _query_transactions(test_transactions[:])
_query_with_futures(test_transactions[:])
