from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.models.model_base import BareBaseModel


class Department(BareBaseModel):
    department_name = Column(String(255), index=True)
    description = Column(Text, nullable=True)
    company_id = Column(Integer, ForeignKey("company.id"))
    parent_id = Column(Integer, ForeignKey("department.id"), nullable=True)
    is_active = Column(Boolean, default=True)

    company = relationship('Company', remote_side='Company.id')
    parent = relationship('Department', remote_side='Department.id')
