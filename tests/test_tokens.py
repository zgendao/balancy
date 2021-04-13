from unittest import mock

import pytest

from app import tokens


@pytest.fixture
def w3():
    return mock.MagicMock()


@pytest.fixture
def crud():
    return mock.MagicMock()


@mock.patch("app.tokens._get_first_block")
@mock.patch("app.tokens._find_contract_creations")
@mock.patch("app.tokens._finish_process")
def test_query_ERC20_tokens(
    _finish_process, _find_contract_creations, _get_first_block, w3, crud
):
    first_block = {"hash": "0x1234", "transactions": []}
    _get_first_block.return_value = first_block
    crud.get_last_block_hash.return_value = None
    w3.get_parent_block.return_value = None

    tokens.query_ERC20_tokens(w3=w3, crud=crud)
    _find_contract_creations.assert_called_once_with(
        w3, crud, first_block["transactions"]
    )
    crud.set_current_block.assert_called_once_with(first_block["hash"])
    w3.get_parent_block.assert_called_once_with(first_block, full_transactions=True)
    _finish_process.assert_called_once()


def test_get_first_block_no_start_block(w3, crud):
    crud.get_start_block_hash.return_value = None
    expected_block = {"hash": "1234"}
    w3.get_latest_block.return_value = expected_block

    result_block = tokens._get_first_block(w3, crud)
    assert result_block == expected_block
    crud.set_start_block.assert_called_once_with(expected_block["hash"])


def test_get_first_block_has_start_block(w3, crud):
    current_block_hash = "1234"
    crud.get_start_block_hash.return_value = "4321"
    crud.get_current_block_hash.return_value = current_block_hash

    expected_block = {"hash": "5678"}
    w3.get_block_by_hash.return_value = expected_block

    result_block = tokens._get_first_block(w3, crud)
    assert result_block == expected_block
    w3.get_block_by_hash.assert_called_once_with(
        current_block_hash, full_transactions=True
    )


@mock.patch("app.tokens._save_if_erc20_token")
def test_find_contract_creations(save_if_erc20, w3, crud):
    num_of_transactions = 42
    transactions = range(num_of_transactions)

    tokens._find_contract_creations(w3, crud, transactions)
    assert save_if_erc20.call_count == num_of_transactions


@mock.patch("app.tokens._save_if_erc20_token")
def test_find_contract_creations_empty_list(save_if_erc20, w3, crud):
    tokens._find_contract_creations(w3, crud, [])
    assert not save_if_erc20.called


def test_save_if_erc20_token(w3, crud):
    transaction = {"hash": "1234"}
    w3.is_transaction_contract_creation.return_value = True
    w3.is_contract_erc20.return_value = True
    contract_address = "some_address"
    w3.get_contract_address_by_transaction_hash.return_value = contract_address

    tokens._save_if_erc20_token(w3, crud, transaction)
    crud.save_token_address.assert_called_once_with(contract_address)


def test_save_if_erc20_token_not_contract(w3, crud):
    transaction = {"hash": "1234"}
    w3.is_transaction_contract_creation.return_value = False

    tokens._save_if_erc20_token(w3, crud, transaction)
    assert not crud.save_token_address.called


def test_save_if_erc20_token_not_erc20(w3, crud):
    transaction = {"hash": "1234"}

    w3.is_transaction_contract_creation.return_value = True
    w3.is_contract_erc20.return_value = False

    tokens._save_if_erc20_token(w3, crud, transaction)
    assert not crud.save_token_address.called
