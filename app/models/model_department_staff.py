from sqlalchemy import Column, Integer, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.model_base import BareBaseModel


class DepartmentStaff(BareBaseModel):
    __tablename__ = 'department_staff'

    department_id = Column(Integer, ForeignKey("department.id"))
    staff_id = Column(Integer, ForeignKey("staff.id"))
    role_title_id = Column(Integer, ForeignKey("role_title.id"), nullable=True)
    is_active = Column(Boolean, default=True)

    department = relationship('Department', remote_side='Department.id')
    staff = relationship('Staff', remote_side='Staff.id')
    role_title = relationship('RoleTitle', remote_side='RoleTitle.id')

    __table_args__ = (
        UniqueConstraint('department_id', 'staff_id', name='_department_staff_unique'),
    )
