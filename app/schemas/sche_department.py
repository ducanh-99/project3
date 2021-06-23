from datetime import datetime
from typing import Optional, Text, List, Any

from pydantic import BaseModel, root_validator, validator

from app.core import error_code, message
from app.helpers.enums import SearchTreeParam
from app.helpers.exception_handler import ValidateException
from app.schemas.sche_company import CompanyIdRequest
from app.helpers.paging import PaginationParams


class DepartmentBase(BaseModel):
    department_name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None

    class Config:
        orm_mode = True


class DepartmentListRequest(CompanyIdRequest, PaginationParams):
    type: Optional[SearchTreeParam] = SearchTreeParam.TREE.value
    department_name: Optional[str]
    parent_id: Optional[int]


class DepartmentItemResponse(DepartmentBase):
    id: int
    department_name: Optional[str]
    count_staffs: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DepartmentDetailResponse(DepartmentBase):
    class DepartmentParent(BaseModel):
        id: int
        department_name: Optional[str]

    class DepartmentCompany(BaseModel):
        id: int
        company_code: Optional[str]
        company_name: Optional[str]

    class DepartmentStaffs(BaseModel):
        id: int
        full_name: Optional[str]
        staff_code: str
        email: str
        phone_number: Optional[str]
        team: List

    id: int
    department_name: Optional[str]
    description: Optional[Text]
    count_staffs: int = 0
    parent: Optional[DepartmentParent]
    company: Optional[DepartmentCompany]
    children: Optional[List[Any]]
    staff: Optional[List[DepartmentStaffs]]
    is_active: Optional[bool]


class DepartmentCreateRequest(CompanyIdRequest, DepartmentBase):
    id: Optional[int]
    department_name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool]

    @validator("department_name", always=True, pre=True)
    def required_department_name(cls, department_name):
        if not department_name:
            raise ValidateException(error_code.ERROR_001_REQUIRED_FIELD_NOT_NULL,
                                    message.MESSAGE_001_REQUIRED_FIELD_NOT_NULL)
        return department_name


class DepartmentAddStaffRequest(BaseModel):
    class DepartmentStaffItem(BaseModel):
        staff_id: int
        role_title_id: int

    department_id: int
    staffs: List[DepartmentStaffItem]

    @root_validator()
    def validate_data(cls, data):
        staffs = data.get("staffs")
        staff_ids = [staff.staff_id for staff in staffs]
        if len(staffs) != len(set(staff_ids)):
            raise ValidateException(
                error_code.ERROR_102_STAFF_ID_DUPLICATE, message.MESSAGE_102_STAFF_ID_DUPLICATE)
        return data


class DepartmentUpdateStaffRequest(BaseModel):
    department_id: int
    staff_id: int
    role_title_id: int
    is_active: bool
