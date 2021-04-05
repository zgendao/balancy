from unittest import mock

import pytest

from app import balances


@pytest.fixture
def w3():
    return mock.MagicMock()


@pytest.fixture
def crud():
    return mock.MagicMock()


def test_fetch_address_token_balances(w3, crud):
    eoa_address = "1234"
    token_addresses = ["012", "345", "678"]
    token_balances = [0, 1, 2]
    crud.get_token_addresses.return_value = token_addresses
    w3.get_eoa_token_balance.side_effect = token_balances

    result = balances.fetch_address_token_balances(eoa_address, w3=w3, crud=crud)
    assert result["address"] == eoa_address
    assert result["processing"] is False
    for address, balance in zip(token_addresses, token_balances):
        assert result[address] == balance

    # should save session_obj at start, end of function + for every address
    expected_save_calls = len(token_addresses) + 2
    assert crud.save_address_balances.call_count == expected_save_calls
