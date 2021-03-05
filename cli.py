import click

from app import web3_client


@click.group()
def main():
    """
    web3 cli tool
    """
    pass


@main.command()
def addresses():
    """Returns eth account addresses"""
    click.echo(web3_client.get_accounts())


@main.command()
@click.argument("address")
def balance(address):
    """Returns balance of an address"""
    click.echo(web3_client.get_eth_balance(address))


if __name__ == "__main__":
    main()
