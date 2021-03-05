from os import getenv

from dotenv import load_dotenv

load_dotenv()


class Config:
    WEB3_PROVIDER = getenv("WEB3_PROVIDER")
    DB_HOST = getenv("DB_HOST")
    DB_PORT = getenv("DB_PORT")


config = Config()
