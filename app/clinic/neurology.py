from .clinic_base import ClinicBase
from app.core.singleton import Singleton


class Neurology(Singleton, ClinicBase):
    id_clinic = 6
    queue = []

    def __init__(self) -> None:
        super().__init__()
