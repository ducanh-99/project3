from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship

from app.models.model_base import BareBaseModel


class Patient(BareBaseModel):

    name = Column(String(255), nullable=False)
    gender = Column(String(255), nullable=False)
    age = Column(String(255), nullable=False)
    diagnostic = Column(String(255), nullable=False)
    disease = Column(String(255))
