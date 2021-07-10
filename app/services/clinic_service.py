from typing import List
from fastapi_sqlalchemy import db

from app.schemas.sche_clinic import ClinicCreate, ClinicItemResponse, ClinicListRequest
from app.models import Clinic
from app.services.base_service import BaseService
from app.helpers.paging import Page, paginate
from app.clinic import list_clinic, Cardiology
from app.clinic.clinic_base import ClinicBase


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
            print(c.get_time_wait())

        return clinic

    def recommend(self, clinics: List[int]):
        time_wait = []
        for clinic_id in clinics:
            clinic = list_clinic[clinic_id-1]
            time_wait.append(clinic.get_time_wait())
        res = [x for _, x in sorted(zip(time_wait, clinics))]

        
        return res


clinic_service = ClinicService()
