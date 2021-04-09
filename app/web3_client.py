from typing import Dict, List, Optional, Union
from urllib.parse import urlparse

from eth_tester.exceptions import TransactionFailed
from hexbytes import HexBytes
from web3 import Web3
from web3.contract import Contract
from web3.exceptions import (
    BadFunctionCallOutput,
    BlockNotFound,
    ContractLogicError,
    InvalidAddress,
    TransactionNotFound,
)
from web3.types import BlockData, ChecksumAddress, TxData

from app.config import EnvConfig

ZERO_HASH = "0x0000000000000000000000000000000000000000000000000000000000000000"

ABI_FUNC_ALLOWANCE = {
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
}

ABI_FUNC_BALANCE_OF = {
    "constant": True,
    "inputs": [{"name": "who", "type": "address"}],
    "name": "balanceOf",
    "outputs": [{"name": "", "type": "uint256"}],
    "payable": False,
    "stateMutability": "view",
    "type": "function",
}

ABI_FUNC_TOTAL_SUPPLY = {
    "constant": True,
    "inputs": [],
    "name": "totalSupply",
    "outputs": [{"name": "", "type": "uint256"}],
    "payable": False,
    "stateMutability": "view",
    "type": "function",
}

ERC20_ABI_VIEWS = [ABI_FUNC_ALLOWANCE, ABI_FUNC_BALANCE_OF, ABI_FUNC_TOTAL_SUPPLY]


class NotFoundException(Exception):
    pass


class ContractNotERC20(Exception):
    pass


class Web3Client:
    def __init__(self, w3: Optional[Web3] = None):
        if w3:
            self.w3 = w3
        else:
            self.w3 = _get_w3(EnvConfig().WEB3_PROVIDER_URL)

    def get_block_by_hash(
        self, hash: Union[str, HexBytes], full_transactions: bool = False
    ) -> BlockData:
        try:
            return self.w3.eth.get_block(hash, full_transactions=full_transactions)
        except (ValueError, BlockNotFound):
            raise NotFoundException

    def get_latest_block(self, full_transactions: bool = False) -> BlockData:
        return self.w3.eth.get_block("latest", full_transactions=full_transactions)

    def get_parent_block(
        self, block: BlockData, full_transactions: bool = False
    ) -> Optional[BlockData]:
        parent_hash = block["parentHash"]
        if parent_hash.hex() == ZERO_HASH:
            return None
        return self.w3.eth.get_block(parent_hash, full_transactions=full_transactions)

    def get_transaction_by_hash(self, hash: Union[str, HexBytes]) -> TxData:
        try:
            return self.w3.eth.get_transaction(hash)
        except (ValueError, TransactionNotFound):
            raise NotFoundException

    def is_transaction_contract_creation(
        self, transaction_hash: Union[str, HexBytes]
    ) -> bool:
        transaction = self.get_transaction_by_hash(transaction_hash)
        return transaction["to"] is None

    def get_contract_address_by_transaction_hash(
        self, hash: Union[str, HexBytes]
    ) -> ChecksumAddress:
        try:
            receipt = self.w3.eth.getTransactionReceipt(hash)
        except (ValueError, TransactionNotFound):
            raise NotFoundException
        contract_address = receipt["contractAddress"]
        if not contract_address:
            raise NotFoundException
        return contract_address

    def get_contract(self, address: ChecksumAddress, abi: List[Dict]) -> Contract:
        try:
            return self.w3.eth.contract(address=address, abi=abi)
        except (InvalidAddress, BadFunctionCallOutput):
            raise NotFoundException

    def is_contract_erc20(self, contract_address: ChecksumAddress) -> bool:
        try:
            contract = self.get_contract(contract_address, ERC20_ABI_VIEWS)
        except NotFoundException:
            return False
        try:
            test_addr = contract_address
            contract.functions.totalSupply().call()
            contract.functions.balanceOf(test_addr).call()
            contract.functions.allowance(test_addr, test_addr).call()
        except (TransactionFailed, BadFunctionCallOutput, ContractLogicError):
            return False
        return True

    def get_eoa_token_balance(self, eoa_address: str, token_address: str) -> int:
        eoa_checksum_addr = self.w3.toChecksumAddress(eoa_address)
        token_checksum_addr = self.w3.toChecksumAddress(token_address)

        contract = self.get_contract(token_checksum_addr, [ABI_FUNC_BALANCE_OF])
        try:
            res = contract.functions.balanceOf(eoa_checksum_addr).call()
        except TransactionFailed:
            raise ContractNotERC20
        return res


def _get_w3(web3_provider_url: Optional[str] = None):
    if not web3_provider_url:
        url = EnvConfig().WEB3_PROVIDER_URL
    else:
        url = web3_provider_url

    parsed_url = urlparse(url)
    if parsed_url.scheme in ("ws", "wss"):
        return Web3(Web3.WebsocketProvider(url))
    elif parsed_url.scheme in ("http", "https"):
        return Web3(Web3.HTTPProvider(url))
    else:
        raise ValueError("invalid scheme for web3 provider url")
