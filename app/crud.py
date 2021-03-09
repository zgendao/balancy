from typing import Any, Optional
from urllib.parse import urlparse

import etcd3

from app.config import config


class Crud:
    def __init__(self, db_uri: Optional[str] = None):
        if not db_uri:
            db_host = config.DB_HOST
            db_port = config.DB_PORT
        else:
            parsed_uri = urlparse(db_uri)
            db_host = parsed_uri.hostname
            db_port = str(parsed_uri.port)
        self.db = etcd3.client(host=db_host, port=db_port)

    def get(self, key: str) -> Any:
        return self.db.get(key)

    def put(self, key: str, value: Any) -> None:
        self.db.put(key, value)

    def delete(self, key: str) -> None:
        self.db.delete(key)
