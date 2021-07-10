from typing import List
from app.schemas.sche_partient import RecommendPatient
from fastapi_sqlalchemy import db

from app.schemas.sche_clinic import ClinicCreate, ClinicItemResponse, ClinicListRequest
from app.models import Patient, ClinicHistory
from app.services.base_service import BaseService
from app.helpers.paging import Page, paginate
from app.clinic import list_clinic
from app.services.clinic_service import clinic_service
from app.services.stored_service import storage


class PatientService(BaseService):

    def __init__(self):
        super().__init__(Patient)

    def recommend(self, patient: RecommendPatient, clinics: List[int]):
        if not patient.id:
            self.add_partient(patient)

        return clinic_service.recommend(clinics)

    def add_partient(self, patient: RecommendPatient):
        new_patient = Patient(
            name=patient.name,
            gender=patient.gender,
            age=patient.age,
            diagnostic=patient.diagnostic,
            disease=patient.disease
        )

        db.session.add(new_patient)
        db.session.commit()


patient_service = PatientService()
