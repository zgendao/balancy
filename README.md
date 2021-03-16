# Balancy

Query balances for certain accounts and more on Ethereum.

**This project is under development! Get back later for more information.**
&nbsp;

## Purpose of the project

- ERC-20 token registry. It means that it has an up-to-date registry about all of the ERC-20 tokens and it is being continously maintained.
    - At first, we query all block's from the 1st block and check all of the transactions. If it's sent to the `0x0` address it means that it's a smart contract. After that we have some rules to determine whether a smart contract is ERC-20 compliant or not. If it is, the contract will be saved into the registry.
    - The last checked block's number will be saved and next time we can continue from that block to look for new ERC-20 contracts.
    - It also checks when was the last activity on that contract. Based on that it sets the status for active or inactive.
    - This tool can be a cronjob running periodically.
- Address balance query. It accepts an Ethereum address and checks the balance for all active ERC-20 contracts stored in the registry. 
    - It will return a session ID because that will take time and the client can ask the status or subscribe on websockets to get notified.
    - This tool can be an API-like solution.

## Project dependencies

#### With poetry:
Run `poetry install` in the project root folder.
#### With pip:
Run `pip install -r requirements.txt`.
&nbsp;

## Using the cli tool:
Inside the project root folder run `python balancy.py --help` for available commands.
For some functions you will have to pass in a web3 provider url and a database uri as flags.
If you have docker installed you can use `docker-compose up` to start an *etcd* database instance and a *ganache* as a web3 test node.
Example commands with docker-compse running:
```console
python balancy.py api --w3url http://127.0.0.1:8545 --db-uri http://127.0.0.1:2379
python balancy.py fetch-token --db-uri http://127.0.0.1:2379 --w3url http://127.0.0.1:8545
```
You want to fork a live node with ganache-cli using docker-compose, you can create a `.env` file and specify the node url inside it like this:
```
WEB3_FORK_URL=<YOUR URL HERE>
```

&nbsp;
## The web api:
You can run the web api with the cli command below:
```console
python balancy.py api -p 8000
```
After the web api started up you can check its available endpoints with the generated OpenAPI docs on this link: http://127.0.0.1:8000/docs#/ (if you are running it on localhost port 8000)

&nbsp;
## Packages and tools:
- https://typer.tiangolo.com/
- https://github.com/kragniz/python-etcd3
- https://web3py.readthedocs.io/en/stable/
- https://github.com/trufflesuite/ganache-cli
- https://python-poetry.org/
