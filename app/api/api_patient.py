from typing import List, Optional
from fastapi import APIRouter, Depends
from fastapi.param_functions import Query
from fastapi.params import Depends


from app.services.clinic_service import ClinicService
from app.services.patient_service import patient_service
from app.schemas.sche_clinic import ClinicCreate, ClinicListRequest
from app.schemas.sche_partient import RecommendPatient, RecommendResponse


router = APIRouter()


@router.post("/recommend", response_model=RecommendResponse)
def recommend(patient = Depends(RecommendPatient), clinics: Optional[List[int]] = Query(default=[])):
    return patient_service.recommend(patient, clinics)


@router.post("/add_clinics")
def add_clinics():
    
    pass


@router.post("/finish_clinic/{id_clinic}")
def finish():
    pass


@router.get("/check_clinic")
def check_clinic():
    pass
