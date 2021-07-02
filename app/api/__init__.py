from fastapi import APIRouter
from .api_clinic import router as clinic_router
router = APIRouter()

router.include_router(clinic_router, prefix='/clinic')
