from sqlalchemy import Column, Integer, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.model_base import BareBaseModel


class ClinicHistory(BareBaseModel):
    __tablename__ = 'clinic_history'

    clinic_id = Column(Integer, ForeignKey("clinic.id"))
    history_id = Column(Integer, ForeignKey("history.id"))

    clinic = relationship('Clinic', remote_side='Clinic.id')
    history_medical = relationship('History', remote_side='History.id')
