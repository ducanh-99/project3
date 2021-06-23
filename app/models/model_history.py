from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime, String

from app.models.model_base import BareBaseModel


class History(BareBaseModel):

    patient_id = Column(Integer, ForeignKey('patient.id'), nullable=False)
    time_start = Column(DateTime, default=datetime.now())
    time_end = Column(DateTime)
    time_predict = Column(DateTime)
    clinic_reality = Column(String(255))
    clinic_predict = Column(String(255))

    patient = relationship('Patient', remote_side='Patient.id')