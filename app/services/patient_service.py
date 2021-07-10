from typing import List
from datetime import datetime
from app.schemas.sche_partient import RecommendPatient
from fastapi_sqlalchemy import db

from app.models import Patient, ClinicHistory, History
from app.services.base_service import BaseService
from app.services.clinic_service import clinic_service
from app.services.stored_service import storage
from app.helpers.paging import Page, paginate
from app.clinic import get_clinic_by_id
from app.schemas.sche_partient import RecommendResponse


class PatientService(BaseService):

    def __init__(self):
        super().__init__(Patient)

    def recommend(self, patient: RecommendPatient, clinics: List[int]):
        if not patient.id:
            new_patient = self.add_partient(patient)
            patient.id = new_patient.id

        clinics, total_wait = clinic_service.recommend(clinics)
        clinis_model = []
        for clinic_id in clinics:
            clinis_model.append(clinic_service.get_by_id(clinic_id))

        self.add_person_to_clinic(id_patient=patient.id, id_clinic=clinics[0])

        return RecommendResponse(total_wait=total_wait, clinis=clinis_model)

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

        return new_patient

    def add_person_to_clinic(self, id_patient, id_clinic):
        clinic = get_clinic_by_id(id_clinic=id_clinic)
        clinic.add_person(id_person=id_patient)

        self.add_history(id_patient=id_patient, id_clinic=id_clinic)

    def add_history(self, id_patient, id_clinic):
        history = History(
            patient_id=id_patient
        )
        db.session.add(history)
        db.session.flush()
        clinic_history = ClinicHistory(
            clinic_id=id_clinic,
            history_id=history.id
        )

        db.session.add(clinic_history)
        db.session.commit()


patient_service = PatientService()
