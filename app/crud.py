import json
from typing import Dict, List, Optional
from urllib.parse import urlparse

import etcd3
from hexbytes import HexBytes

from app.config import EnvConfig

KEY_LAST_BLOCK = "last_block"
KEY_START_BLOCK = "start_block"
KEY_CURRENT_BLOCK = "current_block"
KEY_BLOCK_FETCH = "block_fetch"

PREFIX_TOKEN_ADDRESS = "token"
PREFIX_ADDRESS_BALANCES = "balances"


class Crud:
    def __init__(self):
        parsed_uri = urlparse(EnvConfig().DB_URI)
        db_host = parsed_uri.hostname
        db_port = str(parsed_uri.port)
        self.db = etcd3.client(host=db_host, port=db_port)

    def get_is_block_fetch(self) -> bool:
        return self.db.get(KEY_BLOCK_FETCH)[0] == "1"

    def set_is_block_fetch(self, is_fetch: bool) -> None:
        fetch_status = "1" if is_fetch else "0"
        return self.db.put(KEY_BLOCK_FETCH, fetch_status)

    def set_start_block(self, block_hash: Optional[HexBytes]) -> None:
        self._set_block(KEY_START_BLOCK, block_hash)

    def set_current_block(self, block_hash: Optional[HexBytes]) -> None:
        self._set_block(KEY_CURRENT_BLOCK, block_hash)

    def set_last_block(self, block_hash: Optional[HexBytes]) -> None:
        self._set_block(KEY_LAST_BLOCK, block_hash)

    def get_start_block_hash(self) -> Optional[HexBytes]:
        return self._get_block_hash(KEY_START_BLOCK)

    def get_current_block_hash(self) -> Optional[HexBytes]:
        return self._get_block_hash(KEY_CURRENT_BLOCK)

    def get_last_block_hash(self) -> Optional[HexBytes]:
        return self._get_block_hash(KEY_LAST_BLOCK)

    def save_token_address(self, token_address: str) -> None:
        return self.db.put(f"{PREFIX_TOKEN_ADDRESS}::{token_address}", token_address)

    def get_token_addresses(self) -> List[str]:
        res = self.db.get_prefix(PREFIX_TOKEN_ADDRESS)
        return [token.decode("utf-8") for (token, _) in res]

    def save_address_balances(self, address: str, balances: Dict) -> None:
        self.db.put(f"{PREFIX_ADDRESS_BALANCES}::{address}", json.dumps(balances))

    def get_address_balances(self, address: str) -> Optional[Dict]:
        res = self.db.get(f"{PREFIX_ADDRESS_BALANCES}::{address}")[0]
        try:
            return json.loads(res)
        except (json.JSONDecodeError, TypeError):
            return None

    def _set_block(self, key: str, block_hash: Optional[HexBytes]) -> None:
        if block_hash:
            self.db.put(key, block_hash)
        else:
            self.db.delete(key)

    def _get_block_hash(self, key: str) -> Optional[HexBytes]:
        address = self.db.get(key)[0]
        return HexBytes(address) if address else None
