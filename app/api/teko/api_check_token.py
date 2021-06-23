from fastapi import APIRouter, Depends

from app.helpers.login_manager import AppTokenRequired
from app.schemas.sche_base import ResponseSchemaBase

router = APIRouter()


@router.get("/check-token", dependencies=[Depends(AppTokenRequired('teko'))], response_model=ResponseSchemaBase)
async def get():
    return {
        "code": "000",
        "message": "Teko check token success"
    }