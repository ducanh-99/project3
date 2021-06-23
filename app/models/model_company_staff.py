from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship

from app.models.model_base import BareBaseModel


class CompanyStaff(BareBaseModel):
    __tablename__ = 'company_staff'

    company_id = Column(Integer, ForeignKey("company.id"))
    staff_id = Column(Integer, ForeignKey("staff.id"))
    email = Column(String(255), unique=True, index=True, nullable=False, comment='email staff tương ứng từng cty')
    is_active = Column(Boolean, default=True)

    company = relationship('Company', remote_side='Company.id')
    staff = relationship('Staff', remote_side='Staff.id')
