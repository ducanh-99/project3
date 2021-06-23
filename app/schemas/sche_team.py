from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, root_validator

from app.helpers.paging import PaginationParams
from app.schemas.sche_staff import StaffDetail
from app.schemas.sche_searching_param import SearchingParamSchema
from app.schemas.sche_company import CompanyIdRequest
from app.helpers.exception_handler import CustomException, ValidateException
from app.helpers.validate import validate_team_name
from app.core import error_code, message


class TeamBase(BaseModel):
    team_name: str
    manager_id: Optional[int] = None
    description: Optional[str] = None
    company_id: Optional[int] = None

    class Config:
        orm_mode = True


class TeamListRequest(CompanyIdRequest, PaginationParams):
    search: Optional[str]

    # @root_validator()
    # def validate_data(cls, data):
    #     fields = data.get("field_values").split(
    #         ";") if data.get("field_values") else []

    #     for i in fields:
    #         if i not in ['team_code']:
    #             raise ValidateException(
    #                 error_code.ERROR_006_SEARCH_PARAMS_INVALID, message.MESSAGE_006_SEARCH_PARAMS_INVALID)
    #     return data


class TeamItemResponse(TeamBase):
    id: int
    team_name: Optional[str]
    count_staff: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TeamDetailResponse(TeamItemResponse):
    staffs: Optional[List[StaffDetail]]


class TeamCreateRequest(BaseModel):
    id: Optional[int]
    team_name: Optional[str]
    description: Optional[str] = None
    is_active: Optional[bool] = True
    company_id: Optional[int]

    class Config:
        orm_mode = True

    @root_validator()
    def validate_data(cls, params):
        team_name = params.get("team_name")
        if team_name:
            if not validate_team_name(team_name=team_name):
                raise CustomException(http_code=400, code=error_code.ERROR_163_TEAM_NAME_TOO_LONG, message=message.MESSAGE_163_TEAM_NAME_TOO_LONG)
        return params


class TeamUpdateRequest(BaseModel):
    team_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool]
