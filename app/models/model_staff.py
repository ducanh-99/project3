from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Date, Text
from sqlalchemy.orm import relationship

from app.helpers.enums import StaffContractType
from app.models.model_base import BareBaseModel


class Staff(BareBaseModel):
    full_name = Column(String(255), nullable=True)
    staff_code = Column(String(255), index=True, nullable=False, comment='ma nhan vien')
    date_of_birth = Column(Date, nullable=True, comment='Ngày tháng năm sinh')
    email_personal = Column(String(255), nullable=True, comment='email cá nhân')
    email = Column(String(255), unique=True, index=True, nullable=False, comment='email nhân viên')
    phone_number = Column(String(50), nullable=True, comment='Số điện thoại')
    manager_id = Column(Integer, ForeignKey("staff.id"), nullable=True, comment='ID nguoi quan ly')
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False, comment='ID cong ty')
    date_onboard = Column(Date, nullable=True, comment='Ngày vào công ty')
    bank_name = Column(String(255), nullable=True, comment='tên ngân hàng')
    branch_bank_name = Column(String(255), nullable=True, comment='chi nhánh ngân hàng')
    account_number = Column(String(255), nullable=True, comment='Số tài khoản ngân hàng')
    address_detail = Column(Text, nullable=True, comment='địa chỉ chi tiết')
    identity_card = Column(String(50), nullable=True, comment='Số CMND/CCCD/Hộ chiếu')
    contract_type = Column(String(50), default=StaffContractType.OFFICIAL.value, comment='Thoi vu|Chinh thuc...')
    is_active = Column(Boolean, default=True)
    avatar = Column(String(255), nullable=True, comment="avatar ca nhan")

    manager = relationship('Staff', remote_side='Staff.id')
    company = relationship('Company', remote_side='Company.id')
