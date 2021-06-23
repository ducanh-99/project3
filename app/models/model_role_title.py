from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.models.model_base import BareBaseModel


class RoleTitle(BareBaseModel):
    __tablename__ = 'role_title'

    role_title_name = Column(String(255), index=True, comment='ten chuc danh')
    description = Column(Text, nullable=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    department_id = Column(Integer, ForeignKey('department.id'), nullable=True)
    is_active = Column(Boolean, default=True)

    company = relationship('Company', remote_side='Company.id')
    department = relationship('Department', remote_side='Department.id')
