import typer

from app import web3_client

app = typer.Typer()


@app.command()
def addresses():
    typer.echo(web3_client.get_accounts())


@app.command()
def balance(address: str):
    """Returns balance of an address"""
    typer.echo(web3_client.get_eth_balance(address))


if __name__ == "__main__":
    app()
