from typing import Optional

import typer

from . import balances, tokens
from .crud import Crud
from .web3_client import get_w3

app = typer.Typer()


@app.command()
def say_hello(text: Optional[str] = None):
    message = "General Kenobi!" if text == "Hello there" else "Hi!"
    typer.echo(message)


@app.command()
def find_ERC20_tokens(
    w3url: str = typer.Option(...),
    db_uri: str = typer.Option(...),
):
    w3 = get_w3(w3url)
    crud = Crud(db_uri)
    tokens.query_ERC20_tokens(w3=w3, crud=crud)
    typer.echo("TODO: implement")


@app.command()
def get_token_balance(
    address: str,
    token: str,
    w3url: str = typer.Option(...),
    db_uri: str = typer.Option(...),
):
    w3 = get_w3(w3url)
    crud = Crud(db_uri)
    balances.get_token_balance(address, token, w3=w3, crud=crud)
    typer.echo("TODO: implement")


@app.command()
def addresses(w3url: str = typer.Option(...)):
    """Test function for web3 client. Returns web3 eth addresses."""
    w3 = get_w3(w3url)
    typer.echo(w3.eth.accounts)


@app.command()
def balance(address: str, w3url: str = typer.Option(...)):
    """Test function for web3 client. Returns eth balance of an address."""
    w3 = get_w3(w3url)
    w3.fromWei(w3.eth.get_balance(address), "eth")


@app.command()
def db_put(key: str, val: str, db_uri: str = typer.Option(...)):
    """Test function for db connection."""
    crud = Crud(db_uri)
    crud.put(key, val)
    typer.echo(f"Saved to db with key: {key}!")


@app.command()
def db_get(key: str, db_uri: str = typer.Option(...)):
    """Test function for db connection."""
    crud = Crud(db_uri)
    res = crud.get(key)
    typer.echo(res)
