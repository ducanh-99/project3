from fastapi import APIRouter
from .api_clinic import router as clinic_router
from .api_patient import router as patient_router
router = APIRouter()

router.include_router(clinic_router, tags=["clinic"], prefix='/clinic')
router.include_router(patient_router, tags=["patient"], prefix='/patient')
