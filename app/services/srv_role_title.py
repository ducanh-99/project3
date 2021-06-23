import logging

from fastapi_sqlalchemy import db

from app.helpers.exception_handler import CustomException
from app.models import RoleTitle, Company, Department, DepartmentStaff
from app.core import error_code, message
from app.schemas.sche_role_title import RoleTitleCreateRequest, RoleTitleListRequest, RoleTitleDetailResponse
from app.services.srv_base import BaseService

logger = logging.getLogger()


class RoleTitleService(BaseService):
    def __init__(self):
        super().__init__(RoleTitle)

    def get_list(self, role_title_list_request: RoleTitleListRequest):
        company_id = role_title_list_request.company_id
        _query = db.session.query(self.model).filter(self.model.company_id == company_id)
        if role_title_list_request.role_title_name:
            _query = _query.filter(self.model.role_title_name.ilike(f'%{role_title_list_request.role_title_name}%'))
        if role_title_list_request.department_id:
            _query = _query.filter(self.model.department_id == role_title_list_request.department_id)
        return _query.all()

    def detail(self, role_title_id: int) -> RoleTitleDetailResponse:
        role_title = db.session.query(self.model).get(role_title_id)
        if not role_title:
            raise CustomException(http_code=400, code=error_code.ERROR_191_ROLE_ID_DOES_NOT_EXITS,
                                  message=message.MESSAGE_191_ROLE_ID_DOES_NOT_EXITS)
        return role_title

    def create_or_update(self, req_data: RoleTitleCreateRequest):
        company = db.session.query(Company).get(req_data.company_id)
        if not company:
            raise CustomException(http_code=400, code=error_code.ERROR_061_COMPANY_NOT_FOUND,
                                  message=message.MESSAGE_061_COMPANY_NOT_FOUND)

        if req_data.department_id:
            department = db.session.query(Department).get(req_data.department_id)
            if not department:
                raise CustomException(http_code=400, code=error_code.ERROR_091_DEPARTMENT_ID_NOT_EXISTS,
                                      message=message.MESSAGE_091_DEPARTMENT_ID_NOT_EXISTS)
            if department.company_id != company.id:
                raise CustomException(http_code=400, code=error_code.ERROR_192_DEPARTMENT_NOT_BELONG_TO_COMPANY,
                                      message=message.MESSAGE_192_DEPARTMENT_NOT_BELONG_TO_COMPANY)

        if not req_data.id:
            if req_data.department_id:
                exits_rt = db.session.query(self.model).filter(
                    self.model.department_id == req_data.department_id,
                    self.model.role_title_name == req_data.role_title_name
                ).first()
                if exits_rt:
                    exits_rt.description = req_data.description if req_data.description else exits_rt.description
                    exits_rt.is_active = req_data.is_active if req_data.is_active is not None else exits_rt.is_active
                    db.session.commit()
                    return exits_rt
            new_role_title = RoleTitle(
                role_title_name=req_data.role_title_name,
                description=req_data.description,
                company_id=req_data.company_id,
                department_id=req_data.department_id if req_data.department_id else None,
                is_active=req_data.is_active
            )

            db.session.add(new_role_title)
            db.session.commit()
            return new_role_title
        else:
            exits_rt = db.session.query(self.model).get(req_data.id)
            if req_data.department_id and req_data.department_id != exits_rt.department_id:
                raise CustomException(http_code=400, code=error_code.ERROR_194_CAN_NOT_UPDATE_ROLE_TILE_DEPARTMENT,
                                      message=message.MESSAGE_194_CAN_NOT_UPDATE_ROLE_TILE_DEPARTMENT)
            if req_data.company_id != exits_rt.company_id:
                raise CustomException(http_code=400, code=error_code.ERROR_195_CAN_NOT_UPDATE_ROLE_TILE_COMPANY,
                                      message=message.MESSAGE_195_CAN_NOT_UPDATE_ROLE_TILE_COMPANY)
            if req_data.is_active and exits_rt.department.is_active is False:
                raise CustomException(http_code=400, code=error_code.ERROR_197_CAN_NOT_ACTIVE_ROLE_TILE_IN_DEPARTMENT_INACTIVE,
                                      message=message.MESSAGE_197_CAN_NOT_ACTIVE_ROLE_TILE_IN_DEPARTMENT_INACTIVE)
            if not req_data.is_active:
                count_department_staffs = db.session.query(DepartmentStaff).filter(
                    DepartmentStaff.role_title_id == req_data.id,
                    DepartmentStaff.is_active == True
                ).count()
                if count_department_staffs > 0:
                    raise CustomException(http_code=400, code=error_code.ERROR_193_CAN_NOT_DISABLE_ROLE_TILE,
                                          message=message.MESSAGE_193_CAN_NOT_DISABLE_ROLE_TILE)

            exits_rt.role_title_name = req_data.role_title_name if req_data.role_title_name else exits_rt.role_title_name
            exits_rt.description = req_data.description if req_data.description else exits_rt.description
            exits_rt.is_active = req_data.is_active if req_data.is_active is not None else exits_rt.is_active
            db.session.commit()
            return exits_rt
