from fastapi import APIRouter

from app.api.digi import api_digi

router = APIRouter(tags=['digi'])

router.include_router(api_digi.router, prefix="")
