from fastapi import APIRouter

from app.api.teko import api_check_token

router = APIRouter()

router.include_router(api_check_token.router, tags=["teko"], prefix='')