from typing import List
from app.core.singleton import Singleton


class StoragePatient(Singleton):

    def __init__(self) -> None:
        super().__init__()
        self.stored = {}

    def add_person(self, id: int, clincis: List[int]):
        self.stored[id] = clincis

    
    def remove_clinic(self, id: int) -> List:
        clinic = self.stored.get(id)
        if clinic is None:
            return []
        self.stored[id] = clinic[1:]
        
        return clinic[1:]

storage = StoragePatient()