from .clinic_base import ClinicBase
from app.core.singleton import Singleton


class Gastroenterology(Singleton, ClinicBase):
    id_clinic = 5

    def __init__(self) -> None:
        super().__init__()
