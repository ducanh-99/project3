from typing import Optional, Text

from pydantic import BaseModel

from app.schemas.sche_company import CompanyIdRequest


class RoleTitleBase(BaseModel):
    role_title_name: Optional[str] = None

    class Config:
        orm_mode = True


class RoleTitleListRequest(CompanyIdRequest):
    role_title_name: Optional[str]
    department_id: Optional[int]


class RoleTitleItemResponse(RoleTitleBase):
    id: int
    role_title_name: Optional[str]
    department_id: Optional[int]
    company_id: int
    is_active: bool


class RoleTitleDetailResponse(RoleTitleBase):
    id: int
    description: Optional[Text]
    company_id: int
    department_id: Optional[int]
    is_active: bool


class RoleTitleCreateRequest(RoleTitleBase):
    id: Optional[int]
    role_title_name: str = ''
    description: Optional[str] = None
    company_id: int
    department_id: Optional[int]
    is_active: bool
