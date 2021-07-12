from typing import List
from app.core.singleton import Singleton


class StoragePatient(Singleton):

    def __init__(self) -> None:
        super().__init__()
        self.stored = {}

    def add_patient(self, id_patient: int, clincis: List[int]):
        self.stored[id_patient] = clincis

    def get_clinic(self, id_patient: int):
        clincis = self.stored.get(id_patient)
        if clincis is None:
            return None
        return clincis[0]

    def remove_clinic(self, id: int) -> List:
        clinic = self.stored.get(id)
        if clinic is None:
            return []
        self.stored[id] = clinic[1:]

        return clinic[1:]
    
    def get_clinics(self, id_patient: int):
        clincis = self.stored.get(id_patient)
        if clincis is None:
            return None
        return clincis
    
    def __str__(self) -> str:
        return str(self.stored)


storage = StoragePatient()
