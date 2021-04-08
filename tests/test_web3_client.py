import pytest
from eth_tester import EthereumTester
from web3 import Web3

from app.web3_client import (
    ERC20_ABI_VIEWS,
    ContractNotERC20,
    NotFoundException,
    Web3Client,
    _get_w3,
)

from . import utils


@pytest.fixture(scope="module")
def eth_tester():
    return EthereumTester()


@pytest.fixture(scope="module", name="test_w3")
def w3_for_test(eth_tester):
    return Web3(Web3.EthereumTesterProvider(eth_tester))


@pytest.fixture(scope="module", name="test_transaction", autouse=True)
def create_test_transaction(eth_tester, test_w3):
    accounts = eth_tester.get_accounts()
    hash = eth_tester.send_transaction(
        {"from": accounts[0], "to": accounts[1], "gas": 21000, "value": 42}
    )
    return test_w3.eth.get_transaction(hash)


@pytest.fixture(scope="module", autouse=True)
def create_erc20_contract(test_w3):
    transaction_hash, contract_address = utils.create_contract(
        test_w3, utils.SOURCE_CODE_ERC20_CONTRACT
    )
    return transaction_hash, contract_address


@pytest.fixture(scope="module", autouse=True)
def create_not_erc20_contract(test_w3):
    transaction_hash, contract_address = utils.create_contract(
        test_w3, utils.SOURCE_CODE_NOT_ERC20_CONTRACT
    )
    return transaction_hash, contract_address


@pytest.fixture
def erc20_contract(test_w3, create_erc20_contract):
    _, contract_address = create_erc20_contract
    return test_w3.eth.contract(address=contract_address, abi=ERC20_ABI_VIEWS)


@pytest.fixture
def not_erc20_contract(test_w3, create_not_erc20_contract):
    _, contract_address = create_erc20_contract
    return test_w3.eth.contract(address=contract_address, abi=ERC20_ABI_VIEWS)


@pytest.fixture
def first_block(test_w3):
    return test_w3.eth.get_block(0)


@pytest.fixture
def latest_block(test_w3):
    return test_w3.eth.get_block("latest")


@pytest.fixture(scope="module")
def web3_client(test_w3):
    return Web3Client(test_w3)


@pytest.fixture(name="test_eoa_address")
def get_test_eoa(eth_tester):
    return eth_tester.get_accounts()[0]


@pytest.mark.parametrize(
    "url,expected_provider",
    [
        ("http://127.0.0.1:8545", Web3.HTTPProvider),
        ("https://127.0.0.1:8545", Web3.HTTPProvider),
        ("ws://127.0.0.1:8545", Web3.WebsocketProvider),
        ("wss://127.0.0.1:8545", Web3.WebsocketProvider),
    ],
)
def test_get_w3(url, expected_provider):
    w3 = _get_w3(url)
    assert isinstance(w3.provider, expected_provider)


def test_get_w3_invalid_url_scheme():
    invalid_scheme_url = "asd://127.0.0.1:8545"
    with pytest.raises(ValueError):
        _get_w3(invalid_scheme_url)


class TestWeb3Client:
    def test_get_block_by_hash(self, web3_client, first_block):
        expected_block = first_block
        result_block = web3_client.get_block_by_hash(first_block["hash"])
        assert result_block == expected_block

    def test_get_block_by_hash_invalid_hash(self, web3_client):
        with pytest.raises(NotFoundException):
            web3_client.get_block_by_hash("asd")

    def test_get_latest_block(self, web3_client, latest_block):
        expected_block = latest_block
        result_block = web3_client.get_latest_block()
        assert result_block == expected_block

    def test_get_parent_block(self, web3_client, test_w3, latest_block):
        expected_block = test_w3.eth.get_block(latest_block["parentHash"])
        result_block = web3_client.get_parent_block(latest_block)
        assert result_block == expected_block

    def test_get_parent_block_not_found(self, web3_client, first_block):
        result = web3_client.get_parent_block(first_block)
        assert result is None

    def test_get_transaction_by_hash(self, web3_client, test_transaction):
        hash_str = test_transaction["hash"].hex()
        result = web3_client.get_transaction_by_hash(hash_str)
        expected = test_transaction
        assert result == expected

    def test_get_transaction_by_hash_hex_bytes(self, web3_client, test_transaction):
        hash_hex = test_transaction["hash"]
        result = web3_client.get_transaction_by_hash(hash_hex)
        expected = test_transaction
        assert result == expected

    def test_get_transaction_by_hash_invalid_hash(self, web3_client):
        with pytest.raises(NotFoundException):
            web3_client.get_transaction_by_hash("asd")

    def test_is_transaction_contract_creation_true(
        self, web3_client, test_w3, create_erc20_contract
    ):
        transaction_hash, _ = create_erc20_contract
        assert web3_client.is_transaction_contract_creation(transaction_hash) is True

    def test_is_transaction_contract_creation_false(
        self, web3_client, test_transaction
    ):
        hash = test_transaction["hash"]
        res = web3_client.is_transaction_contract_creation(hash)
        assert res is False

    def test_get_contract_address_by_transaction_hash(
        self, web3_client, create_erc20_contract
    ):
        hash, expected_address = create_erc20_contract
        result_address = web3_client.get_contract_address_by_transaction_hash(hash)
        assert result_address == expected_address

    def test_get_contract_address_by_transaction_hash_not_contract_creation(
        self, web3_client, test_transaction
    ):
        hash = test_transaction["hash"]
        with pytest.raises(NotFoundException):
            web3_client.get_contract_address_by_transaction_hash(hash)

    def test_get_contract(self, web3_client, erc20_contract, create_erc20_contract):
        _, contract_address = create_erc20_contract
        expected = erc20_contract
        result = web3_client.get_contract(contract_address, ERC20_ABI_VIEWS)
        assert result.address == expected.address

    def test_get_contract_invalid_address(self, web3_client):
        with pytest.raises(NotFoundException):
            web3_client.get_contract("invalid_address", ERC20_ABI_VIEWS)

    def test_is_contract_erc20(self, web3_client, create_erc20_contract):
        _, contract_address = create_erc20_contract
        is_erc20 = web3_client.is_contract_erc20(contract_address)
        assert is_erc20 is True

    def test_is_contract_erc20_false(self, web3_client, create_not_erc20_contract):
        _, contract_address = create_not_erc20_contract
        is_erc20 = web3_client.is_contract_erc20(contract_address)
        assert is_erc20 is False

    def test_get_eoa_token_balance(
        self, web3_client, create_erc20_contract, test_eoa_address
    ):
        _, contract_address = create_erc20_contract
        expected_value = 1
        result_value = web3_client.get_eoa_token_balance(
            test_eoa_address, contract_address
        )
        assert result_value == expected_value

    def test_get_eoa_token_balance_invalid_contract(
        self, web3_client, create_not_erc20_contract, test_eoa_address
    ):
        _, contract_address = create_not_erc20_contract
        with pytest.raises(ContractNotERC20):
            web3_client.get_eoa_token_balance(test_eoa_address, contract_address)
