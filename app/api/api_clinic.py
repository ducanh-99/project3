from datetime import time
from app.helpers.paging import C
from fastapi import APIRouter
from fastapi.params import Depends


from app.services.clinic_service import clinic_service
from app.schemas.sche_clinic import ClinicCreate, ClinicListRequest, ClinicDetail
from app.clinic.cardiology import Cardiology

router = APIRouter()


@router.get("", )
async def get(list_clinic_request: ClinicListRequest = Depends()):

    return clinic_service.get_list_clinic(list_clinic_request=list_clinic_request)


@router.post("", deprecated=True)
def create(clinic: ClinicCreate):
    return clinic_service.create_clinic(clinic=clinic)


@router.get("/{id_clinic}", response_model=ClinicDetail)
async def get(id_clinic: int):
    return clinic_service.get_clinic_by_id(id_clinic=id_clinic)
