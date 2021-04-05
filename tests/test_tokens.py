from unittest import mock

import pytest
from hexbytes import HexBytes

from app import tokens


@pytest.fixture
def w3():
    return mock.MagicMock()


@pytest.fixture
def crud():
    return mock.MagicMock()


@mock.patch("app.tokens._get_starting_block")
@mock.patch("app.tokens._find_contract_creations")
def test_query_ERC20_tokens(find_contract_creations, get_starting_block, w3, crud):
    starting_block = {"hash": HexBytes("1234"), "transactions": []}
    get_starting_block.return_value = starting_block
    w3.get_parent_block.return_value = None

    tokens.query_ERC20_tokens(w3=w3, crud=crud)
    find_contract_creations.assert_called_once_with(starting_block["transactions"])
    crud.save_as_earliest_block.assert_called_once_with(starting_block["hash"])
    w3.get_parent_block.assert_called_once_with(starting_block)


def test_get_starting_block_no_earliest_block(w3, crud):
    crud.get_earliest_block_address.return_value = None
    expected_block = {"hash": "1234"}
    w3.get_latest_block.return_value = expected_block

    result_block = tokens._get_starting_block(w3, crud)
    assert result_block == expected_block
    crud.save_as_last_block.assert_called_once_with(expected_block["hash"])


def test_get_starting_block_has_earliest_block(w3, crud):
    earliest_block_hash = HexBytes("1234")
    crud.get_earliest_block_address.return_value = earliest_block_hash

    earliest_block = {"hash": "5678"}
    w3.get_block_by_hash.return_value = earliest_block

    expected_block = {"hash": "9012"}
    w3.get_parent_block.return_value = expected_block

    result_block = tokens._get_starting_block(w3, crud)
    assert result_block == expected_block
    w3.get_block_by_hash.assert_called_once_with(earliest_block_hash)
    w3.get_parent_block.assert_called_once_with(earliest_block)


@mock.patch("app.tokens._save_if_erc20_token")
def test_find_contract_creations(save_if_erc20, w3, crud):
    num_of_transactions = 42
    transactions = [HexBytes(i) for i in range(num_of_transactions)]

    tokens._find_contract_creations(transactions)
    assert save_if_erc20.call_count == num_of_transactions


@mock.patch("app.tokens._save_if_erc20_token")
def test_find_contract_creations_empty_list(save_if_erc20, w3, crud):
    tokens._find_contract_creations([])
    assert not save_if_erc20.called


def test_save_if_erc20_token(w3, crud):
    transaction_hash = HexBytes("1234")
    w3.is_transaction_contract_creation.return_value = True
    w3.is_contract_erc20.return_value = True
    contract_address = "some_address"
    w3.get_contract_address_by_transaction_hash.return_value = contract_address

    tokens._save_if_erc20_token(w3, crud, transaction_hash)
    crud.save_token_address.assert_called_once_with(contract_address)


def test_save_if_erc20_token_not_contract(w3, crud):
    transaction_hash = HexBytes("1234")
    w3.is_transaction_contract_creation.return_value = False

    tokens._save_if_erc20_token(w3, crud, transaction_hash)
    assert not crud.save_token_address.called


def test_save_if_erc20_token_not_erc20(w3, crud):
    transaction_hash = HexBytes("123")

    w3.is_transaction_contract_creation.return_value = True
    w3.is_contract_erc20.return_value = False

    tokens._save_if_erc20_token(w3, crud, transaction_hash)
    assert not crud.save_token_address.called
