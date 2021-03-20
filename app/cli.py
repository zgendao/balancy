import atexit
from typing import Optional

import typer
import uvicorn

from . import tokens
from .config import EnvConfig
from .crud import Crud
from .web3_client import get_w3

app = typer.Typer()


@app.command()
def fetch_tokens(
    w3url: str = typer.Option(None),
    db_uri: str = typer.Option(None),
):
    """Starts searching the blockchain for ERC20 tokens,
    and saves their addresses in the given database."""
    EnvConfig.set_environment(w3url, db_uri)
    w3 = get_w3()
    crud = Crud()
    _setup_is_fetch_status(crud)
    tokens.query_ERC20_tokens(w3=w3, crud=crud)


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


@app.command()
def addresses(w3url: str = typer.Option(None)):
    """Example function, this will be removed later. Returns web3 eth addresses."""
    EnvConfig.set_environment(w3url)
    w3 = get_w3()
    typer.echo(w3.eth.accounts)


@app.command()
def balance(address: str, w3url: str = typer.Option(None)):
    """Example function, this will be removed later.
    Returns eth balance of an address."""
    EnvConfig.set_environment(w3url)
    w3 = get_w3()
    w3.fromWei(w3.eth.get_balance(address), "eth")


@app.command()
def db_put(key: str, val: str, db_uri: str = typer.Option(None)):
    """Example function, this will be removed later. Test function for db connection."""
    EnvConfig.set_environment(db_uri=db_uri)
    crud = Crud()
    crud.put(key, val)
    typer.echo(f"Saved to db with key: {key}!")


@app.command()
def db_get(key: str, db_uri: str = typer.Option(None)):
    """Example function, this will be removed later. Test function for db connection."""
    EnvConfig.set_environment(db_uri=db_uri)
    crud = Crud()
    res = crud.get(key)
    typer.echo(res)
