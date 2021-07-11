from typing import List
from datetime import datetime
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
        self.mean = self.clinic_model.time_mean

    def add_person(self, id_person):
        self.queue.append(id_person)

    def get_person_in_clinic(self) -> int:
        if not self.queue:
            return None
        return self.queue[0]

    def leave_person(self):
        self.queue.pop()
        
    def get_time_wait(self):
        if not self.queue:
            return 0
        first_person = db.query(History).order_by(
            History.id.desc()).filter(History.patient_id == self.queue[0]).first()
        
        return (len(self.queue)-1)*self.mean + datetime.now()-first_person.time_start

    def __str__(self) -> str:
        return str(self.queue)