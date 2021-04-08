import datetime
from typing import Dict

from app.crud import Crud
from app.web3_client import Web3Client


def fetch_address_token_balances(
    eoa_address: str, *, w3: Web3Client, crud: Crud
) -> Dict:
    session_obj = {
        "address": eoa_address,
        "started_at": datetime.datetime.utcnow().timestamp(),
        "processing": True,
    }
    crud.save_address_balances(eoa_address, session_obj)

    token_addresses = crud.get_token_addresses()
    for token_addr in token_addresses:
        balance = w3.get_eoa_token_balance(eoa_address, token_addr)
        session_obj.update({token_addr: balance})
        crud.save_address_balances(eoa_address, session_obj)

    session_obj["processing"] = False
    crud.save_address_balances(eoa_address, session_obj)
    return session_obj
