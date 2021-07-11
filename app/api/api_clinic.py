from datetime import time
from app.helpers.paging import C
from fastapi import APIRouter
from fastapi.params import Depends


from app.services.clinic_service import ClinicService
from app.schemas.sche_clinic import ClinicCreate, ClinicListRequest
from app.clinic.cardiology import Cardiology

router = APIRouter()


@router.get("", )
async def get(list_clinic_request: ClinicListRequest = Depends()):

    return ClinicService().get_list_clinic(list_clinic_request=list_clinic_request)


@router.post("", deprecated=True)
def create(clinic: ClinicCreate):
    return ClinicService().create_clinic(clinic=clinic)


@router.get("/{id_clinic}")
async def get(id_clinic: int, _time: time):
    # from app.models import Clinic
    # from fastapi_sqlalchemy import db
    # clinic = db.session.query(Clinic).filter(Clinic.id == id_clinic).first()
    # clinic.time_mean = _time
    # db.session.commit()
    pass
