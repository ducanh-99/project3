from .clinic_base import ClinicBase
from app.core.singleton import Singleton


class EarNoseThroat(Singleton, ClinicBase):
    id_clinic = 4
    queue = []

    def __init__(self) -> None:
        super().__init__()
