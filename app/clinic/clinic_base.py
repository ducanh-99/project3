from app.models.model_clinic_history import ClinicHistory
from typing import List
from datetime import datetime, date, timedelta
from app.db.base import SessionLocal
from app.models import Clinic, History

db = SessionLocal()


class ClinicBase(object):
    mean: int
    id_clinic: int
    

    def __init__(self) -> None:

        super().__init__()
        self.clinic_model = db.query(Clinic).filter(
            Clinic.id == self.id_clinic).first()
        self.mean = datetime.combine(date.min, self.clinic_model.time_mean) - datetime.min

    def add_person(self, id_person):
        self.queue.append(id_person)

    def get_person_in_clinic(self) -> int:
        if not self.queue:
            return None
        return self.queue[0]

    def leave_person(self):
        self.queue.pop()

    def calculate_mean(self) -> timedelta:
        return (len(self.queue)-1)*self.mean
        
    def get_time_wait(self):
        if not self.queue:
            return timedelta()
        print(self.queue, self.id_clinic)
        first_person = db.query(History)\
            .filter(History.patient_id == self.queue[0])\
            .order_by(History.id.desc())\
            .filter(ClinicHistory.clinic_id == self.id_clinic)\
            .first()
        print(first_person)
        return (len(self.queue)-1)*self.mean

    def __str__(self) -> str:
        return str(self.queue)