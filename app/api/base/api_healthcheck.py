from fastapi import APIRouter

from fastapi import Response

from app.schemas.sche_base import ResponseSchemaBase
from app.helpers.check_database_connect import check_database_connect

router = APIRouter()


@router.get("/live", response_model=ResponseSchemaBase)
async def get():
    return {
        "code": "000",
        "message": "Health check live success"
    }


@router.get("/ready", response_model=ResponseSchemaBase)
async def get():
    is_database_connect, output = check_database_connect()
    return {
        "code": "000",
        "message": "Health check ready success"
    } if is_database_connect else Response({"message": "Health check ready false"}, status_code=400)
