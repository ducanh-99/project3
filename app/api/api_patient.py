from app.schemas.sche_base import DataResponse
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
def recommend(patient=Depends(RecommendPatient), clinics: Optional[List[int]] = Query(default=[])):
    return patient_service.recommend(patient, clinics)


@router.post("/add_clinics")
def add_clinics(id_patient: int):

    patient_service.add_person_to_clinic(id_patient=id_patient)

    return DataResponse().success_response(data={"id": id_patient})


@router.post("/finish_clinic")
def finish(id_patient: int):
    patient_service.remove_person_to_clinic(id_patient=id_patient)
