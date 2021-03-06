from typing import Optional

import typer

from .web3_client import Web3Client

app = typer.Typer()


@app.command()
def say_hello(text: Optional[str] = None):
    message = "General Kenobi!" if text == "Hello there" else "Hi!"
    typer.echo(message)


@app.command()
def addresses(w3url: str = typer.Option(...)):
    """Returns web3 addresses"""
    w3 = Web3Client(w3url)
    typer.echo(w3.get_accounts())


@app.command()
def balance(address: str, w3url: str = typer.Option(...)):
    """Returns balance of an address"""
    w3 = Web3Client(w3url)
    typer.echo(w3.get_eth_balance(address))
