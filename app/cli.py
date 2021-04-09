import atexit
from typing import Optional

import typer
import uvicorn

from . import tokens_v2
from .config import EnvConfig
from .crud import Crud
from .web3_client import Web3Client

app = typer.Typer()


@app.command()
def fetch_tokens(
    w3url: str = typer.Option(None),
    db_uri: str = typer.Option(None),
):
    """Starts searching the blockchain for ERC20 tokens,
    and saves their addresses in the given database."""
    EnvConfig.set_environment(w3url, db_uri)
    w3 = Web3Client()
    crud = Crud()
    _setup_is_fetch_status(crud)
    tokens_v2.query_ERC20_tokens(w3=w3, crud=crud)


def _setup_is_fetch_status(crud: Crud):
    crud.set_is_block_fetch(True)
    atexit.register(crud.set_is_block_fetch, False)


@app.command()
def api(
    w3url: str = typer.Option(None),
    db_uri: str = typer.Option(None),
    port: int = typer.Option(8000, "--port", "-p"),
    auto_reload: bool = typer.Option(False, "--auto-reload", "-r"),
):
    """Starts the web api."""
    EnvConfig.set_environment(w3url, db_uri)

    # With this command uvicorn runs the FastAPI instance
    # named `app` which is located inside app/api.py
    uvicorn.run("app.api:app", port=port, reload=auto_reload)


@app.command()
def set_defaults(
    w3url: str = typer.Option(None),
    db_uri: str = typer.Option(None),
):
    """Sets given w3url and db-uri values as defaults
    by saving them to a .env file. Creates the file if it doesn't exist"""
    if w3url or db_uri:
        EnvConfig.set_defaults(w3url, db_uri)
        typer.echo("Done.")
    else:
        typer.echo("No parameters were given.")


@app.command()
def say_hello(text: Optional[str] = None):
    """Example function, this will be removed later."""
    message = "General Kenobi!" if text == "Hello there" else "Hi!"
    typer.echo(message)
