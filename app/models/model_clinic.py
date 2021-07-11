from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Float, Time
from sqlalchemy.orm import relationship

from app.models.model_base import BareBaseModel


class Clinic(BareBaseModel):

    name = Column(String(255), nullable=False)
    time_mean = Column(Time)
    linear = Column(Float)