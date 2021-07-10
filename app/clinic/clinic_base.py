from typing import List
from app.db.base import SessionLocal
from app.models import Clinic, History

db = SessionLocal()


class ClinicBase(object):
    mean: int
    id_clinic: int
    queue = []

    def __init__(self) -> None:

        super().__init__()
        self.clinic_model = db.query(Clinic).filter(
            Clinic.id == self.id_clinic).first()
        self.mean = self.clinic_model.time_mean

    def add_person(self, id_person):
        self.queue.append(id_person)

    def leave_person(self):
        self.queue.pop()

    
