import json
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import etcd3
from hexbytes import HexBytes

from app.config import EnvConfig

KEY_LAST_BLOCK = "last_block"
KEY_EARLIEST_BLOCK = "earliest_block"
KEY_BLOCK_FETCH = "block_fetch"

PREFIX_TOKEN_ADDRESS = "token"
PREFIX_ADDRESS_BALANCES = "balances"


class Crud:
    def __init__(self):
        parsed_uri = urlparse(EnvConfig().DB_URI)
        db_host = parsed_uri.hostname
        db_port = str(parsed_uri.port)
        self.db = etcd3.client(host=db_host, port=db_port)

    def get(self, key: str) -> Any:
        return self.db.get(key)[0]

    def put(self, key: str, value: Any) -> None:
        self.db.put(key, value)

    def delete(self, key: str) -> None:
        self.db.delete(key)

    def get_is_block_fetch(self) -> bool:
        return self.db.get(KEY_BLOCK_FETCH)[0] == "1"

    def set_is_block_fetch(self, is_fetch: bool) -> None:
        fetch_status = "1" if is_fetch else "0"
        return self.db.put(KEY_BLOCK_FETCH, fetch_status)

    def save_as_last_block(self, block_address: HexBytes) -> None:
        self.db.put(KEY_LAST_BLOCK, block_address)

    def save_as_earliest_block(self, block_address: HexBytes) -> None:
        self.db.put(KEY_EARLIEST_BLOCK, block_address)

    def get_last_block_address(self) -> Optional[HexBytes]:
        address = self.db.get(KEY_LAST_BLOCK)[0]
        return HexBytes(address) if address else None

    def get_earliest_block_address(self) -> Optional[HexBytes]:
        address = self.db.get(KEY_EARLIEST_BLOCK)[0]
        return HexBytes(address) if address else None

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
