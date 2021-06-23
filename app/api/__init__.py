from fastapi import APIRouter
from .base.router import router as base_router
from .teko.api_router import router as teko_router
from .digi.api_router import router as digi_router

router = APIRouter()

router.include_router(base_router, prefix='/api')
