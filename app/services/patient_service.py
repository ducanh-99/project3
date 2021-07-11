from typing import List
from datetime import datetime
from app.schemas.sche_partient import RecommendPatient
from fastapi_sqlalchemy import db

from app.models import Patient, ClinicHistory, History
from app.services.base_service import BaseService
from app.services.clinic_service import clinic_service
from app.services.stored_service import storage
from app.helpers.exception_handler import CustomException
from app.clinic import get_clinic_by_id, list_clinic
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

        # self.add_person_to_clinic(id_patient=patient.id, id_clinic=clinics[0])

        storage.add_patient(id_patient=patient.id, clincis=clinics)

        return RecommendResponse(total_wait=total_wait, clinis=clinis_model, id_patient=patient.id)

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

    def add_person_to_clinic(self, id_patient):
        id_clinic = storage.get_clinic(id_patient=id_patient)
        if id_clinic is None:
            raise CustomException(http_code=400, code='001',
                                  message='Bệnh nhân chưa được chỉ định')
        clinic = get_clinic_by_id(id_clinic=id_clinic)
        clinic.add_person(id_person=id_patient)

        self.add_history(id_patient=id_patient, id_clinic=id_clinic)

    def remove_person_to_clinic(self, id_patient):
        id_clinic = storage.get_clinic(id_patient=id_patient)

        clinic = get_clinic_by_id(id_clinic=id_clinic)

        if clinic.get_person_in_clinic() == id_patient:
            clinic.leave_person()
            self.update_time_end(id_patient=id_patient, id_clinic=id_clinic)
            storage.remove_clinic(id=id_patient)

    def update_time_end(self, id_patient, id_clinic):
        history = db.session.query(History)\
            .join(ClinicHistory)\
            .filter(History.patient_id == id_patient)\
            .order_by(History.id.desc())\
            .filter(ClinicHistory.clinic_id == id_clinic)\
            .first()
        history.time_end = datetime.now()
        db.session.commit()

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
