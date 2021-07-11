from .clinic_base import ClinicBase
from app.core.singleton import Singleton


class Nutrition(Singleton, ClinicBase):
    id_clinic = 7
    queue = []

    def __init__(self) -> None:
        super().__init__()
