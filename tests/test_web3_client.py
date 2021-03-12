import pytest
from web3 import Web3

from app.web3_client import get_w3


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
    w3 = get_w3(url)
    assert isinstance(w3.provider, expected_provider)


def test_get_w3_invalid_url_scheme():
    invalid_scheme_url = "asd://127.0.0.1:8545"
    with pytest.raises(ValueError):
        get_w3(invalid_scheme_url)
