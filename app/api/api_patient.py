from app.helpers.paging import C
from fastapi import APIRouter
from fastapi.params import Depends


from app.services.clinic_service import ClinicService
from app.schemas.sche_clinic import ClinicCreate, ClinicListRequest


router = APIRouter()


@router.post("/recommend")
def recommend():
    pass


@router.post("/add_clinics")
def add_clinics():
    pass


@router.post("/finish_clinic/{id_clinic}")
def finish():
    pass


@router.get("/check_clinic")
def check_clinic():
    pass
