from datetime import date
from typing import Optional, List

from pydantic import BaseModel, EmailStr
from pydantic.class_validators import root_validator

from app.helpers.exception_handler import CustomException, ValidateException
from app.helpers.paging import PaginationParams
from app.helpers.validate import validate_card, validate_phone_number
from app.schemas.sche_searching_param import SearchingParamSchema
from app.schemas.sche_company import CompanyIdRequest
from app.helpers.enums import SearchTreeParam
from app.core import error_code, message

REGEX = '(84|0[3|5|7|8|9])+([0-9]{8})\b'


class Company(BaseModel):
    id: int
    email: EmailStr


class StaffBase(BaseModel):
    full_name: Optional[str]
    staff_code: Optional[str]
    email: Optional[EmailStr]
    phone_number: Optional[str]
    companies: Optional[List[Company]]
    is_active: Optional[bool] = True

    @root_validator()
    def params_valid(cls, params):
        phone_number = params.get("phone_number")
        if phone_number:
            validate_phone_number(phone_number)
        identity_card = params.get("identity_card")
        if identity_card:
            validate_card(card=identity_card)

        return params


class StaffCreateUpdateRequest(StaffBase):
    class Department(BaseModel):
        department_id: Optional[int]
        role_title_id: Optional[int]
        is_active: Optional[bool]

    class Teams(BaseModel):
        team_id: Optional[int] = None
        is_active: Optional[bool] = True

    id: Optional[int]
    date_of_birth: Optional[date]
    email_personal: Optional[EmailStr]
    manager_id: Optional[int]
    date_onboard: Optional[date]
    bank_name: Optional[str]
    branch_bank_name: Optional[str]
    account_number: Optional[str]
    address_detail: Optional[str]
    identity_card: Optional[str]
    contract_type: Optional[str]
    department: Optional[Department]
    teams: Optional[List[Teams]]
    avatar: Optional[str]

    @root_validator()
    def params_valid(cls, params):
        id = params.get('id')
        if not id and id != 0:
            res = []
            full_name = params.get('full_name')
            res.append('full_name') if not full_name else None
            staff_code = params.get('staff_code')
            res.append('staff_code') if not staff_code else None
            email = params.get('email')
            res.append('email') if not email else None
            phone_number = params.get('phone_number')
            res.append('phone_number') if not phone_number else None
            companies = params.get('companies')
            res.append('companies') if not companies or len(
                companies) == 0 else None
            is_active = params.get('is_active')
            res.append('is_active') if not is_active else None
            department = params.get('department')
            res.append('department') if not department else None
            if len(res) > 0:
                raise CustomException(http_code=400, code=error_code.ERROR_001_REQUIRED_FIELD_NOT_NULL,
                                      message=message.MESSAGE_001_REQUIRED_FIELD_NOT_NULL)
        return params


class StaffTeamItem(BaseModel):
    id: int

    class Config:
        orm_mode = True


class StaffsRequest(BaseModel):
    team_id: int
    staffs: List[StaffTeamItem]


class StaffRequest(BaseModel):
    team_id: int
    staff_id: int
    is_active: Optional[bool]


class StaffList(BaseModel):
    team_id: int
    staffs: List[StaffTeamItem]


class StaffDetail(BaseModel):
    staff_code: Optional[str]
    full_name: Optional[str]
    email: Optional[EmailStr]
    phone_number: Optional[str]
    department: Optional[str]
    is_active: Optional[bool]


class StaffCreate(BaseModel):
    staff_code: Optional[EmailStr]
    email: Optional[str]


class StaffListRequest(CompanyIdRequest, PaginationParams):
    type: Optional[SearchTreeParam] = SearchTreeParam.TREE.value
    search: Optional[str]
    parent_node: Optional[int]

    # department_id: Optional[int]
    # team_id: Optional[int]
    # manager_id: Optional[int]

    @root_validator()
    def validate_data(cls, data):
        type = data.get("type").value
        fields = data.get("field_values").split(
            ";") if data.get("field_values") else []

        if type not in [e.value for e in SearchTreeParam]:
            raise ValidateException(
                error_code.ERROR_051_SEARCH_PARAM_TYPE_FAIL, message.MESSAGE_051_SEARCH_PARAM_TYPE_FAIL)

        return data


class StaffItemResponse(BaseModel):
    id: int
    full_name: str
    staff_code: str
    email: EmailStr
    phone_number: str
    manager_id: Optional[int]


class StaffAddDepartment(BaseModel):
    staff_id: int
    role_title_id: int


class StaffUploadFileRequest(CompanyIdRequest):
    file_path: str


class StaffUploadFileResponse(BaseModel):
    total_rows: Optional[int]
    file_path: Optional[str]
