from typing import Any

from app.db import etcd


class Crud:
    def get(self, key: str) -> Any:
        return etcd.get(key)

    def put(self, key: str, value: Any) -> None:
        etcd.put(key, value)

    def delete(self, key: str) -> None:
        etcd.delete(key)


crud = Crud()
