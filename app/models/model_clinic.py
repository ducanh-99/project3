from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, Float
from sqlalchemy.orm import relationship

from app.models.model_base import BareBaseModel


class Clinic(BareBaseModel):

    name = Column(String(255), nullable=False)
    time_mean = Column(Float)
    linear = Column(Float)