from .clinic_base import ClinicBase
from app.core.singleton import Singleton


class Cardiology(Singleton, ClinicBase):
    id_clinic = 1
    queue = []

    def __init__(self) -> None:
        super().__init__()
