from app.models.model_patient import Patient
from app.helpers.exception_handler import CustomException
from app.models.model_clinic_history import ClinicHistory
from datetime import date, datetime, timedelta
from app.models.model_history import History
from typing import List
from fastapi_sqlalchemy import db

from app.schemas.sche_clinic import ClinicCreate, ClinicDetail, ClinicItemResponse, ClinicListRequest
from app.models import Clinic
from app.services.base_service import BaseService
from app.helpers.paging import Page, paginate
from app.clinic import get_clinic_by_id, list_clinic, Cardiology
from app.clinic.clinic_base import ClinicBase


# def get_history(id_pa):


class ClinicService(BaseService):

    def __init__(self):
        super().__init__(Clinic)

    def create_clinic(self, clinic: ClinicCreate):
        clinic_new = Clinic(name=clinic.name)
        db.session.add(clinic_new)
        db.session.commit()
        return clinic_new

    def get_list_clinic(self, list_clinic_request: ClinicListRequest) -> Page[ClinicItemResponse]:
        _query = db.session.query(Clinic)

        clinic = paginate(model=self.model, query=_query,
                          params=list_clinic_request)

        for c in list_clinic:
            print(id(c.queue))
        return clinic

    def recommend(self, clinics: List[int]):
        time_wait = []
        for clinic_id in clinics:
            clinic = list_clinic[clinic_id-1]
            time_wait.append(self.get_time_wait(clinic=clinic))
        # res = [x for _, x in sorted(zip(time_wait, clinics))]
        time_wait, clinics = zip(*sorted(zip(time_wait, clinics)))
        if len(set(time_wait)) == 1:
            list_mean = self.get_list_mean_clinic(id_clinics=clinics)
            list_mean, clinics = zip(*sorted(zip(list_mean, clinics)))
        return clinics, max(time_wait)

    def get_time_wait(self, clinic: ClinicBase) -> timedelta:
        if not clinic.queue:
            return timedelta()
        # print(self.queue, self.id_clinic)
        first_person = db.session.query(History)\
            .join(ClinicHistory)\
            .filter(History.patient_id == clinic.get_person_in_clinic())\
            .order_by(History.id.desc())\
            .filter(ClinicHistory.clinic_id == clinic.id_clinic)\
            .first()
        return clinic.calculate_mean() + datetime.now() - first_person.time_start
    
    def get_by_id(self, id) -> Clinic:
        return db.session.query(self.model).filter(self.model.id == id).first()
    
    def get_clinic_by_id(self, id_clinic):
        clinic_model = self.get_by_id(id=id_clinic)
        if not clinic_model:
            raise CustomException(http_code=400, code='001', message='phòng khám không tồn tại')
        clinic = get_clinic_by_id(id_clinic=id_clinic)
        clinic_model = clinic_model.__dict__
        clinic_model['patients'] = self.get_patient_in_list(list_patient=clinic.get_list_patient())

        return clinic_model

    def get_patient_in_list(self, list_patient: List[int]):
        return db.session.query(Patient).filter(Patient.id.in_(list_patient)).all()
    
    def get_list_mean_clinic(self, id_clinics):
        res = []
        for id_clinic in id_clinics:
            time_mean = self.get_by_id(id=id_clinic).time_mean
            time_delta = datetime.combine(date.min, time_mean) - datetime.min
            res.append(time_delta)
        return res



clinic_service = ClinicService()
