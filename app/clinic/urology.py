from .clinic_base import ClinicBase
from app.core.singleton import Singleton


class Urology(Singleton, ClinicBase):
    id_clinic = 10

    def __init__(self) -> None:
        super().__init__()
