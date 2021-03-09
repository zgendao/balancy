import os
from typing import Optional

import typer
import uvicorn

from . import tokens
from .crud import Crud
from .web3_client import get_w3

app = typer.Typer()


@app.command()
def fetch_tokens(
    w3url: str = typer.Option(...),
    db_uri: str = typer.Option(...),
):
    """Starts searching the blockchain for ERC20 tokens,
    and saves their addresses in the given database."""
    w3 = get_w3(w3url)
    crud = Crud(db_uri)
    tokens.query_ERC20_tokens(w3=w3, crud=crud)
    typer.echo("TODO: implement")


@app.command()
def api(
    w3url: str = typer.Option("http://127.0.0.1:8545"),
    db_uri: str = typer.Option("http://127.0.0.1:2379"),
    port: int = typer.Option(8000, "--port", "-p"),
    auto_reload: bool = typer.Option(False, "--auto-reload", "-r"),
):
    """Starts the web api."""
    os.environ["WEB3_PROVIDER"] = w3url
    os.environ["DB_URI"] = db_uri

    uvicorn.run("app.api:app", port=port, reload=auto_reload)


@app.command()
def say_hello(text: Optional[str] = None):
    """Example function, this will be removed later."""
    message = "General Kenobi!" if text == "Hello there" else "Hi!"
    typer.echo(message)


@app.command()
def addresses(w3url: str = typer.Option(...)):
    """Example function, this will be removed later. Returns web3 eth addresses."""
    w3 = get_w3(w3url)
    typer.echo(w3.eth.accounts)


@app.command()
def balance(address: str, w3url: str = typer.Option(...)):
    """Example function, this will be removed later.
    Returns eth balance of an address."""
    w3 = get_w3(w3url)
    w3.fromWei(w3.eth.get_balance(address), "eth")


@app.command()
def db_put(key: str, val: str, db_uri: str = typer.Option(...)):
    """Example function, this will be removed later. Test function for db connection."""
    crud = Crud(db_uri)
    crud.put(key, val)
    typer.echo(f"Saved to db with key: {key}!")


@app.command()
def db_get(key: str, db_uri: str = typer.Option(...)):
    """Example function, this will be removed later. Test function for db connection."""
    crud = Crud(db_uri)
    res = crud.get(key)
    typer.echo(res)
