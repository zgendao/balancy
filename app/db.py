import etcd3

from app.config import config

etcd = etcd3.client(host=config.DB_HOST, port=config.DB_PORT)
