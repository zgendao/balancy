from fastapi import BackgroundTasks, FastAPI, Response, status

from app import balances
from app.crud import Crud
from app.web3_client import Web3Client

w3 = Web3Client()
crud = Crud()


app = FastAPI()


@app.get("/addresses/{address}")
async def find_balances(
    *,
    address: str,
    tasks: BackgroundTasks,
):
    tasks.add_task(balances.fetch_address_token_balances, address, w3=w3, crud=crud)
    return {"session_id": address}


@app.get("/sessions/{id}")
async def get_session(
    *,
    id: str,
    response: Response,
):
    res = crud.get_address_balances(id)
    if not res:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Session not found"}
    return res
