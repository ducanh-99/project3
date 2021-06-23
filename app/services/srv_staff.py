import io
from datetime import datetime, timedelta
import copy

import collections
import numpy as np
import pandas as pd

from io import BytesIO
from typing import Dict, List, Any
from fastapi_sqlalchemy import db

from pydantic.networks import EmailStr
from sqlalchemy.sql.elements import literal, or_
from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import count, func
from app.helpers.exception_handler import CustomException
from app.helpers.minio_handler import MinioHandler
from app.helpers.time_helper import get_current_time
from app.models import Department, Company, Staff, DepartmentStaff, Team, StaffTeam, CompanyStaff, RoleTitle, Base
from app.helpers.validate import validate_email, validate_phone
from app.core import error_code, message
from app.services.srv_base import BaseService
from app.helpers.enums import StaffContractType
from app.schemas.sche_staff import StaffCreateUpdateRequest, StaffItemResponse, StaffListRequest, StaffAddDepartment, \
    StaffUploadFileRequest
from app.schemas.sche_department import DepartmentUpdateStaffRequest
from app.helpers.paging import Page, paginate
from app.services.srv_department import DepartmentService
from app.services.srv_team import TeamService


COLUMNS = ['Fullname', 'StaffCode', 'Email', 'Phone'	, 'DepartmentID',
           'DepartmentName', 'TitleName', 'TeamName',	'LineManagerEmail']
COLUMNS_ERROR = ['Fullname', 'StaffCode', 'Email', 'Phone'	, 'DepartmentID',
                 'DepartmentName', 'TitleName', 'TeamName',	'LineManagerEmail', 'DS lỗi (xóa cột này khi import)']
FULL_NAME = 0
STAFF_CODE = 1
EMAIL = 2
PHONE = 3
DEPARTMENT_ID = 4
DEPARTMENT_NAME = 5
TITLE_NAME = 6
TEAM_NAME = 7
LINE_MANAGER_EMAIL = 8
ERROR = 9


class StaffService(BaseService):

    def __init__(self):
        super().__init__(Staff)
        self.upload_excel_validate = True
        self.total_columns = 0

    @staticmethod
    def create_or_update_staff_to_department(staff_company_id, req_data: DepartmentUpdateStaffRequest):
        if req_data is None:
            return
        department = db.session.query(Department).get(req_data.department_id)
        if not department or not department.is_active:
            raise CustomException(http_code=400, code=error_code.ERROR_091_DEPARTMENT_ID_NOT_EXISTS,
                                  message=message.MESSAGE_091_DEPARTMENT_ID_NOT_EXISTS)
        if department.company_id != staff_company_id:
            raise CustomException(http_code=400, code=error_code.ERROR_097_STAFF_AND_DEPARTMENT_NOT_SAME_COMPANY,
                                  message=message.MESSAGE_097_STAFF_AND_DEPARTMENT_NOT_SAME_COMPANY)
        DepartmentService.validate_list_role_title(
            department=department, role_title_ids=[req_data.role_title_id])

        depart_in_com = db.session.query(Department).filter(
            Department.company_id == staff_company_id,
            Department.is_active == True
        ).all()

        exists_department_staffs = db.session.query(DepartmentStaff).filter(
            DepartmentStaff.department_id.in_(
                [depart.id for depart in depart_in_com]),
            DepartmentStaff.staff_id == req_data.staff_id,
        ).all()

        # Trong 1 công ty. nếu Staff chưa thuộc Department nào thì tạo mới Department-Staff
        if len(exists_department_staffs) == 0:
            new_department_staff = DepartmentStaff(
                department_id=department.id,
                staff_id=req_data.staff_id,
                role_title_id=req_data.role_title_id,
                is_active=req_data.is_active
            )
            db.session.add(new_department_staff)
            return
        # Trong 1 công ty. nếu Staff đã thuộc Department (bất kể trạng thái)
        department_staff_active = None
        for exists_department_staff in exists_department_staffs:
            if exists_department_staff.is_active:
                department_staff_active = exists_department_staff
                break
        # với department active có 2 trường hợp
        if department_staff_active:
            # trùng với department cũ
            if department_staff_active.department_id == department.id:
                department_staff_active.role_title_id = req_data.role_title_id if req_data.role_title_id else department_staff_active.role_title_id
                department_staff_active.is_active = req_data.is_active if req_data.is_active is not None else department_staff_active.is_active
                return
            # deactive department cũ đi
            department_staff_active.is_active = False
        # Nếu đã tồn tại nhân viên trong phòng ban trước đó rồi thì update
        for exists_department_staff in exists_department_staffs:
            if exists_department_staff.staff_id == req_data.staff_id and exists_department_staff.department_id == req_data.department_id:
                exists_department_staff.role_title_id = req_data.role_title_id if req_data.role_title_id else exists_department_staff.role_title_id
                exists_department_staff.is_active = req_data.is_active if req_data.is_active is not None else exists_department_staff.is_active
                return
        # còn lại thì tạo mới
        new_department_staff = DepartmentStaff(
            department_id=department.id,
            staff_id=req_data.staff_id,
            role_title_id=req_data.role_title_id,
            is_active=req_data.is_active
        )
        db.session.add(new_department_staff)

    def create(self, staff_create_request: StaffCreateUpdateRequest):
        if len(staff_create_request.companies) < 1:
            raise CustomException(
                http_code=400, error_code='140', message='Chưa chọn company chính')
        self._validate_common(data=staff_create_request)
        self._validate_create(data=staff_create_request)

        company_id = next(
            company.id for company in staff_create_request.companies if
            company.email == staff_create_request.email)
        new_staff = Staff(
            full_name=staff_create_request.full_name,
            staff_code=staff_create_request.staff_code,
            email=staff_create_request.email,
            phone_number=staff_create_request.phone_number,
            is_active=staff_create_request.is_active,
            # search company_id
            company_id=company_id,
            date_of_birth=staff_create_request.date_of_birth if staff_create_request.date_of_birth else None,
            email_personal=staff_create_request.email_personal if staff_create_request.email_personal else None,
            manager_id=staff_create_request.manager_id if staff_create_request.manager_id else None,
            date_onboard=staff_create_request.date_onboard if staff_create_request.date_onboard else None,
            bank_name=staff_create_request.bank_name if staff_create_request.bank_name else None,
            branch_bank_name=staff_create_request.branch_bank_name if staff_create_request.branch_bank_name else None,
            account_number=staff_create_request.account_number if staff_create_request.account_number else None,
            address_detail=staff_create_request.address_detail if staff_create_request.address_detail else None,
            identity_card=staff_create_request.identity_card if staff_create_request.identity_card else None,
            contract_type=staff_create_request.contract_type if staff_create_request.contract_type else StaffContractType.OFFICIAL.value,
            avatar=staff_create_request.avatar if staff_create_request.avatar else None,
            created_at=get_current_time(),
            updated_at=get_current_time()
        )
        db.session.add(new_staff)
        db.session.flush()
        # add company-staff
        self._add_company_staff(
            companies=staff_create_request.companies, staff_id=new_staff.id)
        department_staff = DepartmentUpdateStaffRequest(
            department_id=staff_create_request.department.department_id,
            staff_id=new_staff.id,
            role_title_id=staff_create_request.department.role_title_id,
            is_active=staff_create_request.department.is_active if staff_create_request.department.is_active is not None else True
        )
        StaffService.create_or_update_staff_to_department(
            staff_company_id=company_id, req_data=department_staff)
        team_service = TeamService()
        team_service.add_staff_to_teams(
            staff_id=new_staff.id, teams=staff_create_request.teams)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise CustomException(
                http_code=400, code=error_code.ERROR_999_SERVER, message=message.MESSAGE_999_SERVER)
        return new_staff.id

    def _validate_create(self, data: StaffCreateUpdateRequest):

        # validate email
        if data.email:
            staff = self._get_by_email(data.email)
            if staff:
                raise CustomException(http_code=400, code=error_code.ERROR_122_EMAIL_ALREADY_EXISTS,
                                      message=message.MESSAGE_122_EMAIL_ALREADY_EXISTS)
        # Check staff code
        staff_exists = db.session.query(self.model).filter(
            self.model.staff_code == data.staff_code).first()
        if staff_exists:
            raise CustomException(http_code=400, code='135',
                                  message="Mã nhân viên trùng nhau")

        email = self._get_company_email(
            email=data.email, companies=data.companies)
        if not email:
            raise CustomException(http_code=400, code=error_code.ERROR_126_EMAIL_COMPANY_INVALID,
                                  message=message.MESSAGE_126_EMAIL_COMPANY_INVALID)
        # validate manager
        if data.manager_id:
            company_id = self._get_company_id(
                email=data.email, companies=data.companies)
            manager = self._get_by_id(id=data.manager_id)
            if manager.company_id != company_id:
                raise CustomException(http_code=400, code=error_code.ERROR_129_MANAGER_ID_INVALID,
                                      message=message.MESSAGE_129_MANAGER_ID_INVALID)

    def _validate_update(self, data: StaffCreateUpdateRequest, staff_db):
        # validate email
        if data.email:
            staff = self._get_by_email(data.email)
            if staff and staff.id != staff_db.id:
                raise CustomException(http_code=400, code=error_code.ERROR_122_EMAIL_ALREADY_EXISTS,
                                      message=message.MESSAGE_122_EMAIL_ALREADY_EXISTS)
        # Check staff code
        staff_exists = db.session.query(self.model).filter(
            self.model.staff_code == data.staff_code).first()
        if staff_exists and staff_exists.id != staff_db.id:
            raise CustomException(http_code=400, code=error_code.ERROR_135_STAFF_CODE_DUPLICATE,
                                  message=message.MESSAGE_135_STAFF_CODE_DUPLICATE)
        # validate manager
        if data.manager_id:
            staff = self._get_by_id(id=data.id)
            manager = self._get_by_id(id=data.manager_id)
            if staff.company_id != manager.company_id:
                raise CustomException(http_code=400, code=error_code.ERROR_129_MANAGER_ID_INVALID,
                                      message=message.MESSAGE_129_MANAGER_ID_INVALID)

    def _validate_common(self, data: StaffCreateUpdateRequest):

        # validate exists company
        if data.companies:
            for company in data.companies:
                company_exists = db.session.query(Company).filter(
                    Company.id == company.id).first()
                if not company_exists:
                    raise CustomException(http_code=400, code=error_code.ERROR_061_COMPANY_NOT_FOUND,
                                          message=message.MESSAGE_061_COMPANY_NOT_FOUND)

        # validate manager id
        if data.manager_id:
            staff_exists = self._get_by_id(id=data.manager_id)
            if not staff_exists or not staff_exists.is_active:
                raise CustomException(http_code=400, code=error_code.ERROR_130_MANAGER_NOT_FOUND,
                                      message=message.MESSAGE_130_MANAGER_NOT_FOUND)

    @staticmethod
    def delete_staff_in_model(staff_id, object: Base):
        objects = db.session.query(object).filter(
            object.staff_id == staff_id, object.is_active).all()
        for obj in objects:
            obj.is_active = False

    def delete_staff(self, staff_id):
        self.delete_staff_in_model(staff_id=staff_id, object=CompanyStaff)
        self.delete_staff_in_model(staff_id=staff_id, object=StaffTeam)
        self.delete_staff_in_model(staff_id=staff_id, object=DepartmentStaff)

    def _get_company_id(self, email: str, companies):
        for company in companies:
            if email == company.email:
                return company.id
        return None

    def _get_company_email(self, email: str, companies):
        if companies == None:
            return None
        for company in companies:
            if email == company.email:
                return email
        return None

    def _get_by_email(self, email) -> Staff:
        staff_exists = db.session.query(self.model).filter(
            self.model.email == email).first()
        return staff_exists

    def _get_by_id(self, id) -> Staff:
        staff_exists = db.session.query(self.model).filter(
            self.model.id == id).first()
        return staff_exists

    def _add_company_staff(self, companies, staff_id: int):
        company_staffs = db.session.query(CompanyStaff).filter(
            CompanyStaff.staff_id == staff_id).all()
        for company_entity in company_staffs:
            companies = [company for company in companies if not (
                company['id'] == company_entity.company_id)]
        res = []
        for company in companies:
            res.append(
                CompanyStaff(
                    company_id=company.id,
                    staff_id=staff_id,
                    email=company.email
                )
            )

        db.session.add_all(res)

    def update(self, staff_update_request: StaffCreateUpdateRequest):
        staff = self._get_by_id(id=staff_update_request.id)
        if not staff:
            raise CustomException(http_code=400, code=error_code.ERROR_134_STAFF_ID_NOT_FOUND,
                                  message=message.MESSAGE_134_STAFF_ID_NOT_FOUND)
        list_children = self.get_list_children(
            manager_id=staff.id, company_id=staff.company_id)
        self._validate_common(data=staff_update_request)
        self._validate_update(data=staff_update_request, staff_db=staff)
        self._validate_manager_id_belong_child(
            manager_id=staff_update_request.manager_id, list_children=list_children)
        self._validate_inactive_staff(
            list_children=list_children, is_active=staff_update_request.is_active)

        # update team
        team_service = TeamService()
        team_service.update_staff_in_teams(
            staff_id=staff.id, teams=staff_update_request.teams)

        # update department
        if staff_update_request.department is not None:
            department_staff = DepartmentUpdateStaffRequest(
                department_id=staff_update_request.department.department_id,
                staff_id=staff_update_request.id,
                role_title_id=staff_update_request.department.role_title_id,
                is_active=staff_update_request.department.is_active if staff_update_request.department.is_active is not None else True
            )
            StaffService.create_or_update_staff_to_department(
                staff_company_id=staff.company_id, req_data=department_staff)
        # check delete staff
        if staff_update_request.is_active == False:
            self.delete_staff(staff_id=staff_update_request.id)
        staff.full_name = staff_update_request.full_name if staff_update_request.full_name else staff.full_name
        staff.staff_code = staff_update_request.staff_code if staff_update_request.staff_code else staff.staff_code
        staff.email = staff_update_request.email if staff_update_request.email else staff.email
        staff.phone_number = staff_update_request.phone_number if staff_update_request.phone_number else staff.phone_number
        staff.is_active = staff_update_request.is_active if staff_update_request.is_active != None else staff.is_active
        # search company_id
        staff.date_of_birth = staff_update_request.date_of_birth if staff_update_request.date_of_birth else staff.date_of_birth
        staff.email_personal = staff_update_request.email_personal if staff_update_request.email_personal else staff.email_personal
        staff.manager_id = staff_update_request.manager_id if staff_update_request.manager_id is not None else None
        staff.date_onboard = staff_update_request.date_onboard if staff_update_request.date_onboard else staff.date_onboard
        staff.bank_name = staff_update_request.bank_name if staff_update_request.bank_name else staff.bank_name
        staff.branch_bank_name = staff_update_request.branch_bank_name if staff_update_request.branch_bank_name else staff.branch_bank_name
        staff.account_number = staff_update_request.account_number if staff_update_request.account_number else staff.account_number
        staff.address_detail = staff_update_request.address_detail if staff_update_request.address_detail else staff.address_detail
        staff.identity_card = staff_update_request.identity_card if staff_update_request.identity_card else staff.identity_card
        staff.contract_type = staff_update_request.contract_type if staff_update_request.contract_type else StaffContractType.OFFICIAL.value
        staff.avatar = staff_update_request.avatar if staff_update_request.avatar else staff.avatar
        staff.updated_at = get_current_time()
        db.session.commit()

    def get_list_children(self, manager_id, company_id) -> List[Staff]:
        list_children = []
        all_staffs = self._query_all_staff(company_id=company_id)
        node_staff = self._get_by_id(manager_id)

        def recursion(node_staff: Staff, all_staffs: List[Staff]):
            nonlocal list_children
            children = list(
                filter(lambda staff: staff.manager_id == node_staff.id, all_staffs))
            for child in children:
                list_children.append(child)
                recursion(node_staff=child, all_staffs=all_staffs)

        recursion(node_staff=node_staff, all_staffs=all_staffs)
        return list_children

    def _validate_manager_id_belong_child(self, manager_id, list_children: List[Staff]):
        if manager_id is None:
            return
        for child in list_children:
            if child.id == manager_id:
                raise CustomException(http_code=400, code=error_code.ERROR_136_MANAGER_ID_BELONG_CHILDREN,
                                      message=message.MESSAGE_136_MANAGER_ID_BELONG_CHILDREN)

    def _validate_inactive_staff(self, list_children, is_active):
        if is_active is None:
            return
        if not is_active and len(list_children) > 0:
            raise CustomException(
                http_code=400, code=error_code.ERROR_137_MANAGER_CANNOT_INACTIVE,
                message=message.MESSAGE_137_MANAGER_CANNOT_INACTIVE)

    def _query_all_staff(self, company_id: int) -> List[Staff]:
        all_staffs = db.session.query(self.model).filter(self.model.company_id == company_id,
                                                         self.model.is_active == True).with_entities(
            self.model.id,
            self.model.full_name,
            self.model.staff_code,
            self.model.email,
            self.model.phone_number,
            self.model.manager_id,
            self.model.created_at,
            self.model.updated_at
        ).all()

        return all_staffs

    def add_fields_manager(self, all_staffs=[]):
        _query = db.session.query(self.model)
        for index, staff in enumerate(all_staffs):
            staff["manager"] = None
            # if staff["manager_id"] != None:
            manager = _query.filter(
                self.model.id == staff["manager_id"]).first()
            staff["manager"] = {}
            staff["manager"]["id"] = manager.id if manager else None
            staff["manager"]["full_name"] = manager.full_name if manager else None
            staff["manager"]["email"] = manager.email if manager else None
            del staff["manager_id"]
            all_staffs[index] = staff

        return all_staffs

    def add_fields_department(self, all_staffs=[]):
        _query_department = db.session.query(Department). \
            join(DepartmentStaff). \
            filter(Department.id == DepartmentStaff.department_id)
        for index, staff in enumerate(all_staffs):
            department = _query_department.filter(
                DepartmentStaff.staff_id == staff["id"], DepartmentStaff.is_active).first()
            role_title = db.session.query(RoleTitle). \
                join(DepartmentStaff). \
                filter(DepartmentStaff.department_id == RoleTitle.department_id,
                       DepartmentStaff.staff_id == staff["id"], DepartmentStaff.is_active).first()
            staff["department"] = {}
            staff["department"]["department_id"] = department.id if department else None
            staff["department"]["department_name"] = department.department_name if department else None
            staff["department"]["role_title"] = role_title.role_title_name if role_title else None
            staff["department"]["role_title_id"] = role_title.id if role_title else None
            # role_title = _query.filter(
            #     DepartmentStaff.staff_id == staff["id"]).first()
            # staff["title"] = role_title.role_title_name if role_title else None
            all_staffs[index] = staff
        return all_staffs

    def add_list_team(self, all_staffs=[]):
        _query_team = db.session.query(Team).filter(
            Team.is_active).join(StaffTeam)
        for index, staff in enumerate(all_staffs):
            teams = _query_team.filter(
                StaffTeam.staff_id == staff["id"], StaffTeam.is_active).all()
            staff["team"] = []
            for team in teams:
                staff["team"].append(
                    {"team_id": team.id, "team_name": team.team_name})
            all_staffs[index] = staff
        return all_staffs

    def add_list_company(self, all_staffs=[]):
        _query_company = db.session.query(CompanyStaff).join(Company)
        for index, staff in enumerate(all_staffs):
            companies = _query_company.filter(
                CompanyStaff.staff_id == staff["id"], CompanyStaff.is_active) \
                .with_entities(
                CompanyStaff.company_id,
                CompanyStaff.email,
                Company.company_name
            ) \
                .all()
            staff["companies"] = []
            for company in companies:
                staff["companies"].append(
                    {"id": company.company_id, "email": company.email,
                     "company_name": company.company_name}
                )
            all_staffs[index] = staff
        return all_staffs

    def get_tree(self, company_id: int):
        self._check_company_exists(company_id=company_id)
        all_staffs = self._query_all_staff(company_id=company_id)
        # convert to dict
        all_staffs = [dict(staff) for staff in all_staffs]
        all_staffs = self.add_fields_manager(all_staffs=all_staffs)
        all_staffs = self.add_fields_department(all_staffs=all_staffs)
        all_staffs = self.add_list_team(all_staffs=all_staffs)
        root_staffs = list(
            filter(lambda staff: not staff['manager']["id"], all_staffs))

        for i in range(len(root_staffs)):
            childrens, count_staff = self.get_children_with_count_staff(
                node_staff=root_staffs[i], all_staffs=all_staffs)
            root_staffs[i]['children'] = childrens
            root_staffs[i]['count_staff'] = count_staff - 1
        return root_staffs

    def get_children(self, node_staff: Staff, all_staffs: List[Staff]):
        children = list(filter(
            lambda staff: staff['manager']["id"] == node_staff['id'], all_staffs))
        for i in range(len(children)):
            children[i]['children'] = self.get_children(
                node_staff=children[i], all_staffs=all_staffs)

        return children

    def get_children_with_count_staff(self, node_staff: Staff, all_staffs: List[Staff]):
        children = list(filter(
            lambda staff: staff['manager']["id"] == node_staff['id'], all_staffs))
        count_staff = 0
        for i in range(len(children)):
            children[i]['children'], staff_children = self.get_children_with_count_staff(
                node_staff=children[i], all_staffs=all_staffs)
            count_staff += staff_children
        node_staff['count_staff'] = count_staff
        return children, count_staff + 1

    def _check_company_exists(self, company_id):
        company_exists = db.session.query(Company).filter(
            Company.id == company_id).first()
        if not company_exists:
            raise CustomException(http_code=400, code=error_code.ERROR_061_COMPANY_NOT_FOUND,
                                  message=message.MESSAGE_061_COMPANY_NOT_FOUND)

    def get_list_with_paging(self, staff_list_req: StaffListRequest, external_param: Dict) -> Page[StaffItemResponse]:
        self._check_company_exists(company_id=staff_list_req.company_id)
        _query = None
        if staff_list_req.parent_node:
            hierarchy = db.session.query(
                self.model, literal(0).label('level')) \
                .filter(self.model.manager_id == staff_list_req.parent_node) \
                .cte(name="hierarchy", recursive=True)

            parent = aliased(hierarchy, name="p")
            children = aliased(self.model, name="c")
            hierarchy = hierarchy.union_all(
                db.session.query(
                    children,
                    (parent.c.level + 1).label("level"))
                .filter(children.manager_id == parent.c.id))

            _query = db.session.query(self.model, hierarchy.c.level) \
                .select_entity_from(hierarchy)
        if _query is None:
            _query = db.session.query(self.model)
        _query = _query.filter(
            self.model.company_id == staff_list_req.company_id, self.model.is_active == True).with_entities(
            self.model.id,
            self.model.full_name,
            self.model.staff_code,
            self.model.email,
            self.model.phone_number,
            self.model.manager_id,
            self.model.created_at,
            self.model.updated_at
        )
        if staff_list_req.search:
            value = staff_list_req.search
            _query = _query.filter(
                or_(
                    self.model.email.ilike('%' + value + '%'),
                    self.model.full_name.ilike('%' + value + '%'),
                    self.model.staff_code.ilike('%' + value + '%'),
                    self.model.phone_number.ilike('%' + value + '%'),
                )
            )

        if external_param["department_id"] != []:
            department_id = external_param["department_id"]
            departments = db.session.query(DepartmentStaff).filter(
                DepartmentStaff.department_id.in_(department_id), DepartmentStaff.is_active).all()
            staff_in = [department.staff_id for department in departments]
            _query = _query.filter(
                self.model.id.in_(staff_in)
            )
        if external_param["team_id"] != []:
            team_id = external_param["team_id"]
            teams = db.session.query(StaffTeam).filter(
                StaffTeam.team_id.in_(team_id), StaffTeam.is_active).all()

            staff_in = [team.staff_id for team in teams]
            _query = _query.filter(
                self.model.id.in_(staff_in)
            )
        if external_param["manager_id"] != []:
            manager_id = external_param["manager_id"]
            _query = _query.filter(
                self.model.manager_id.in_(manager_id))
        staffs = paginate(
            model=self.model, query=_query, params=staff_list_req)
        staffs.data = [dict(element) for element in staffs.data]
        staffs.data = self.add_fields_manager(all_staffs=staffs.data)
        staffs.data = self.add_fields_department(all_staffs=staffs.data)
        staffs.data = self.add_list_team(all_staffs=staffs.data)
        return staffs

    def get_detail(self, staff: Staff):
        all_staffs = db.session.query(self.model).filter(self.model.company_id == staff.company_id).filter(self.model.is_active).with_entities(
            self.model.id,
            self.model.full_name,
            self.model.staff_code,
            self.model.email,
            self.model.phone_number,
            self.model.manager_id,
            self.model.created_at,
            self.model.updated_at
        ).all()
        # convert to response
        all_staffs = [dict(staff) for staff in all_staffs]
        all_staffs = self.add_fields_manager(all_staffs=all_staffs)
        all_staffs = self.add_fields_department(all_staffs=all_staffs)
        all_staffs = self.add_list_team(all_staffs=all_staffs)
        staff = staff.__dict__
        staff = self.add_fields_manager(all_staffs=[staff])
        staff = self.add_fields_department(all_staffs=staff)[0]
        staff['children'], count_staff = self.get_children_with_count_staff(
            node_staff=staff, all_staffs=all_staffs)
        staff['count_staff'] = count_staff - 1
        staff = self.add_list_team(all_staffs=[staff])[0]
        staff = self.add_list_company(all_staffs=[staff])[0]
        return staff

    def get_detail_with_tree(self, id: int):
        staff = db.session.query(self.model).filter(
            self.model.id == id).first()
        if not staff:
            raise CustomException(http_code=400, code=error_code.ERROR_134_STAFF_ID_NOT_FOUND,
                                  message=message.MESSAGE_134_STAFF_ID_NOT_FOUND)
        staff = self.get_detail(staff=staff)
        return staff

    def get_detail_with_email(self, email: EmailStr):
        staff = db.session.query(self.model).filter(
            self.model.email == email).first()
        if not staff:
            raise CustomException(http_code=400, code=error_code.ERROR_121_EMAIL_NOT_FOUND,
                                  message=message.MESSAGE_121_EMAIL_NOT_FOUND)
        staff = self.get_detail(staff=staff)
        return staff

    def upload_excel(self, req_data: StaffUploadFileRequest):
        self.upload_excel_validate = True
        self._check_company_exists(company_id=req_data.company_id)
        dfs, self.total_columns = self._upload_excel_read_file(
            file_path=req_data.file_path)
        data_rows = dfs.values.tolist()
        data_rows = self._upload_excel_validate_full_name(data_rows=data_rows)
        data_rows = self._upload_excel_validate_staff_code(data_rows=data_rows)
        data_rows = self._upload_excel_validate_staffs(data_rows=data_rows)
        data_rows = self._upload_excel_validate_phone(data_rows=data_rows)
        data_rows = self._upload_excel_validate_departments(
            data_rows=data_rows)
        data_rows = self._upload_excel_validate_role_name(data_rows=data_rows)
        data_rows = self._upload_excel_validate_team_name(
            company_id=req_data.company_id, data_rows=data_rows)
        data_rows = self._upload_excel_validate_line_manager(
            company_id=req_data.company_id, data_rows=data_rows)

        if self.upload_excel_validate:
            self._insert_staff_data(
                company_id=req_data.company_id, data=dfs.values.tolist())
            db.session.commit()
            return len(data_rows), None
        else:
            data_file = self._upload_excel_write_error_file(
                list_data=data_rows)
            return len(data_rows), data_file['file_name']

    @staticmethod
    def _upload_excel_read_file(file_path: str):
        minio_client = MinioHandler().get_instance()
        if not minio_client.check_file_name_exists(minio_client.bucket_name, file_path):
            raise CustomException(http_code=400, code=error_code.ERROR_045_FORMAT_FILE,
                                  message=message.MESSAGE_045_FORMAT_FILE)

        file_ext = file_path.split('.')[-1]
        if file_ext.lower() not in ('xlsx', 'xls', 'csv'):
            raise CustomException(http_code=400, code=error_code.ERROR_045_FORMAT_FILE,
                                  message=message.MESSAGE_045_FORMAT_FILE)

        file = minio_client.client.get_object(
            minio_client.bucket_name, file_path)
        column_names = COLUMNS
        converters = {column: str for column in column_names}
        dfs = pd.read_excel(io.BytesIO(file.read()),
                            sheet_name=0, converters=converters)
        if len(dfs.columns.tolist()) != len(column_names) or len(dfs.values.tolist()) > 5000:
            raise CustomException(http_code=400, code=error_code.ERROR_139_FILE_WRONG_TEMPLATE,
                                  message=message.MESSAGE_139_FILE_WRONG_TEMPLATE)
        return dfs.replace(np.nan, '', regex=True), len(dfs.columns.tolist())

    @staticmethod
    def _upload_excel_write_error_file(list_data: List[Any]):
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df = pd.DataFrame(list_data,
                          columns=COLUMNS_ERROR)
        df.to_excel(writer, index=False)
        writer.save()

        data_file = MinioHandler().get_instance().put_object(
            file_name='error_file.xlsx',
            file_data=BytesIO(output.getvalue()),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        return data_file

    # def check_if_none(self, data_rows, type):
    #     for row in data_rows:
    #         if row[type].strip() == '':

    def _upload_excel_validate_full_name(self, data_rows: list) -> list:
        for row in data_rows:
            if row[FULL_NAME].strip() == '':
                if len(row) == ERROR:
                    row.append('Tên không được để trống')
        return data_rows

    def _upload_excel_validate_staff_code(self, data_rows: list) -> list:
        staff_code = [staff_row[STAFF_CODE] for staff_row in data_rows if len(
            staff_row) == self.total_columns]
        for row in data_rows:
            if row[STAFF_CODE].strip() == '':
                if len(row) == ERROR:
                    row.append('Staff Code không được để trống')

        if len(staff_code) != len(set(staff_code)):
            self.upload_excel_validate = False
            for row in data_rows:
                if row[STAFF_CODE] in [item for item, count in collections.Counter(staff_code).items() if count > 1]:
                    if len(row) == ERROR:  # Nếu dòng chưa có lỗi
                        row.append('Staff Code bị duplicate')
        staff_code_exists = db.session.query(Staff).filter(
            Staff.staff_code.in_(staff_code)).all()
        if len(staff_code_exists) > 0:
            self.upload_excel_validate = False
            for row in data_rows:
                if row[STAFF_CODE] in [e.staff_code for e in staff_code_exists]:
                    if len(row) == ERROR:  # Nếu dòng chưa có lỗi
                        row.append('Staff Code đã tồn tại trong hệ thống')

        return data_rows

    def _upload_excel_validate_staffs(self, data_rows: list) -> list:
        staff_emails = [staff_row[EMAIL] for staff_row in data_rows if len(
            staff_row) == self.total_columns]

        for row in data_rows:
            if row[EMAIL].strip() == '':
                if len(row) == ERROR:
                    row.append('Email không được để trống')
            if not validate_email(row[EMAIL].strip()):
                if len(row) == ERROR:
                    row.append('Email sai định dạng ')

        if len(staff_emails) != len(set(staff_emails)):
            self.upload_excel_validate = False
            for row in data_rows:
                if row[EMAIL] in [item for item, count in collections.Counter(staff_emails).items() if count > 1]:
                    if len(row) == ERROR:  # Nếu dòng chưa có lỗi
                        row.append('Email bị duplicate')

        email_exists = db.session.query(CompanyStaff).filter(
            CompanyStaff.email.in_(staff_emails)).all()
        if len(email_exists) > 0:
            self.upload_excel_validate = False
            for row in data_rows:
                if row[EMAIL] in [e.email for e in email_exists]:
                    if len(row) == ERROR:  # Nếu dòng chưa có lỗi
                        row.append('Email đã tồn tại trong hệ thống')
        return data_rows

    def _upload_excel_validate_phone(self, data_rows: list) -> list:
        phones = [staff_row[PHONE] for staff_row in data_rows if len(
            staff_row) == self.total_columns]
        phone_errors = []
        for phone in phones:
            if not validate_phone(phone):
                phone_errors.append(phone)
        if len(phone_errors):
            self.upload_excel_validate = False
            for row in data_rows:
                if row[PHONE] in phone_errors:
                    if len(row) == ERROR:  # Nếu dòng chưa có lỗi
                        row.append('Số điện thoại sai định dạng')
        return data_rows

    def _upload_excel_validate_departments(self, data_rows: list) -> list:
        department_ids = [staff_row[DEPARTMENT_ID] for staff_row in data_rows if len(
            staff_row) <= self.total_columns]

        wrong_department_ids = []
        for department_id in department_ids:
            if not department_id.isdigit() or department_id.strip() == '':
                wrong_department_ids.append(department_id)
        # wrong_department_ids = [
        #     department_id for department_id in department_ids if not department_id.isdigit() or department_id.strip() == '']
        if len(wrong_department_ids) > 0:
            self.upload_excel_validate = False
            for row in data_rows:
                if row[DEPARTMENT_ID] in wrong_department_ids or row[DEPARTMENT_ID].strip() == '':
                    if len(row) == ERROR:  # Nếu dòng chưa có lỗi
                        row.append(
                            'DepartmentID lỗi định dạng hoặc không được bỏ trống')

        department_exists = db.session.query(Department).filter(
            Department.id.in_([int(i) for i in np.setdiff1d(
                department_ids, wrong_department_ids)]),
            Department.is_active == True).all()
        not_exists_department_ids = np.setdiff1d(
            [int(i) for i in np.setdiff1d(department_ids, wrong_department_ids)],
            [dept.id for dept in department_exists])
        if len(not_exists_department_ids) > 0:
            self.upload_excel_validate = False
            for row in data_rows:
                if row[DEPARTMENT_ID].strip() == '':
                    continue
                if int(row[DEPARTMENT_ID]) in not_exists_department_ids:
                    if len(row) == ERROR:  # Nếu dòng chưa có lỗi
                        row.append(
                            'DepartmentID không tồn tại hoặc đang bị khóa')
        return data_rows

    def _upload_excel_validate_role(self, data_rows: list) -> list:
        data_role_ids = [staff_row[6] for staff_row in data_rows if len(
            staff_row) <= self.total_columns]
        wrong_format_role_ids = [
            item for item in data_role_ids if not item.isdigit()]
        if len(wrong_format_role_ids) > 0:
            self.upload_excel_validate = False
            for row in data_rows:
                if row[6] in wrong_format_role_ids or row[6].strip() == '':
                    if len(row) == self.total_columns:  # Nếu dòng chưa có lỗi
                        row.append(
                            'Title ID sai định dạng hoặc không được bỏ trống')

        role_titles = db.session.query(RoleTitle).filter(
            RoleTitle.id.in_(
                [int(item) for item in data_role_ids if item not in wrong_format_role_ids]),
            RoleTitle.is_active == True).all()
        for row in data_rows:
            if len(list(filter(lambda rt: str(rt.id) == row[6] and str(rt.department_id) == row[4], role_titles))) != 1:
                self.upload_excel_validate = False
                if len(row) == self.total_columns:
                    row.append('Title ID không tồn tại hoặc đã bị khóa')

        return data_rows

    @staticmethod
    def get_role_title_id_with_role_title_name(department_id: int,  role_title_name: str):
        role_title = db.session.query(RoleTitle).filter(
            RoleTitle.department_id == department_id, RoleTitle.role_title_name.ilike(f'{role_title_name}'), RoleTitle.is_active).first()
        return role_title.id

    def _upload_excel_validate_role_name(self, data_rows: list) -> list:
        for row in data_rows:
            if row[TITLE_NAME].strip() == '':
                if len(row) == self.total_columns:  # Nếu dòng chưa có lỗi
                    row.append(
                        'Title Name sai định dạng hoặc không được bỏ trống')

        for row in data_rows:
            if len(row) == len(COLUMNS_ERROR):
                continue
            title_name = row[TITLE_NAME].strip()

            query_role_title = db.session.query(RoleTitle).filter(RoleTitle.role_title_name.ilike(f'{title_name}'))
            role_title = query_role_title.filter(RoleTitle.is_active).first()
            if role_title is None:
                self.upload_excel_validate = False
                if len(row) == self.total_columns:
                    row.append('Title Name không tồn tại hoặc đã bị khóa')

            role_title_exists = query_role_title.filter(RoleTitle.department_id == row[DEPARTMENT_ID]).first()
            if role_title_exists is None:
                self.upload_excel_validate = False
                if len(row) == self.total_columns:
                    row.append('Title Name không thuộc phòng ban')

            role_title_inactive = query_role_title.filter(
                RoleTitle.is_active).first()
            if role_title_inactive is None:
                self.upload_excel_validate = False
                if len(row) == self.total_columns:
                    row.append('Title Name không tồn tại hoặc đã bị khóa')

        return data_rows

    def _upload_excel_validate_team(self, data_rows: list) -> list:
        team_rows = [staff_row[8] for staff_row in data_rows if len(
            staff_row) <= self.total_columns]
        for row in data_rows:
            team_ids = [item.strip() for item in row[8].split(',')]
            for team_id in team_ids:
                if row[8].strip() == '':
                    continue
                if not team_id.isdigit():
                    self.upload_excel_validate = False
                    if len(row) == self.total_columns:  # Nếu dòng chưa có lỗi
                        row.append('Team ID sai định dạng')
                        if row[8] in team_rows:
                            team_rows.remove(row[8])

        list_team_ids = []
        for team in team_rows:
            for team_id in [item.strip() for item in team.split(',') if item.strip() != '']:
                list_team_ids.append(
                    team_id)
        team_id_exists = [data.id for data in
                          db.session.query(Team).filter(Team.id.in_(list_team_ids), Team.is_active == True).all()]
        for row in data_rows:
            if row[8].strip() == '':
                continue
            if len(row) == self.total_columns:  # Nếu dòng chưa có lỗi
                team_ids = [int(item.strip()) for item in row[8].split(',')]
                if not set(team_ids).issubset(team_id_exists):
                    self.upload_excel_validate = False
                    row.append('Team Name không tồn tại hoặc đã bị khóa')

        return data_rows

    @staticmethod
    def get_team_id_with_name(name: str, company_id: int):
        team = db.session.query(Team).filter(Team.is_active, Team.team_name.ilike(
            f'{name}'), Team.company_id == company_id).first()
        if team is None:
            return None
        return team.id

    def _upload_excel_validate_team_name(self, company_id: int,  data_rows: list) -> list:
        for row in data_rows:
            team_names = [item.strip() for item in row[TEAM_NAME].split(',')]
            for team_name in team_names:
                if row[TEAM_NAME].strip() == '':
                    continue
                team_id = self.get_team_id_with_name(
                    name=team_name, company_id=company_id)
                if team_id is None and len(row) == self.total_columns:
                    row.append('Team Name không tồn tại hoặc đã bị khóa')

        return data_rows

    def get_children_with_excel(self, email: str, data_rows: list) -> list:
        children = []

        def recursion(data_rows, email):
            nonlocal children
            for row in data_rows:
                if row[LINE_MANAGER_EMAIL].strip() == email and email != '':
                    email_child = row[EMAIL].strip()
                    children.append(email_child)
                    recursion(data_rows=data_rows, email=email_child)
        email = email.strip()
        recursion(data_rows=data_rows, email=email)
        return children

    def _upload_excel_validate_line_manager(self, company_id: int, data_rows: list) -> list:
        for row in data_rows:
            if row[2].strip() == row[LINE_MANAGER_EMAIL].strip() and len(row) == self.total_columns:
                self.upload_excel_validate = False
                row.append('Line Manager Email trùng Staff email')

        staff_emails = [staff_row[2].strip() for staff_row in data_rows]
        manager_emails = [staff_row[LINE_MANAGER_EMAIL].strip()
                          for staff_row in data_rows]
        list_manager_email_exists = [manager.email for manager in
                                     db.session.query(CompanyStaff).filter(
                                         CompanyStaff.email.in_(
                                             manager_emails),
                                         CompanyStaff.company_id == company_id).all()]
        for row in data_rows:
            if row[LINE_MANAGER_EMAIL].strip() == '':
                continue
            if row[LINE_MANAGER_EMAIL].strip() not in list_manager_email_exists and row[LINE_MANAGER_EMAIL].strip() not in staff_emails:
                if len(row) == self.total_columns:
                    self.upload_excel_validate = False
                    row.append(
                        'Line Manager Email không tồn tại trong file và trong hệ thống')
            copy_data_rows_with_not_current_row = copy.deepcopy(data_rows)
            copy_data_rows_with_not_current_row.remove(row)
            children = self.get_children_with_excel(
                data_rows=copy_data_rows_with_not_current_row, email=row[EMAIL])
            if row[LINE_MANAGER_EMAIL].strip() in children:
                if len(row) == self.total_columns:
                    self.upload_excel_validate = False
                    row.append(
                        'Line Manager Email không đưọc dưới quyền của nhân viên')
        return data_rows

    @staticmethod
    def _upload_excel_write_log(data):
        pass

    def _insert_staff_data(self, company_id: int, data: list):
        """
        Includes 5 step:
        => Bulk insert staff
        => bulk insert company-staff
        => bulk update manager
        => bulk insert department-staff
        => bulk insert team-staff
        """
        # 1. Bulk insert staff
        staff_list_mappings = [Staff(
            full_name=staff[0],
            staff_code=staff[1],
            email=staff[2],
            phone_number=staff[3],
            company_id=company_id,
        ) for staff in data]
        db.session.bulk_save_objects(staff_list_mappings, return_defaults=True)
        db.session.flush()
        id_staff_mappings = {
            staff.email: staff.id for staff in staff_list_mappings}

        # 2. Bulk insert company_staff
        insert_company_staff_mappings = [CompanyStaff(
            company_id=company_id,
            staff_id=staff.id,
            email=staff.email
        ) for staff in staff_list_mappings]
        db.session.bulk_save_objects(insert_company_staff_mappings)

        # 3. Bulk update staff - line manager
        managers = db.session.query(Staff).filter(
            Staff.email.in_([manager[LINE_MANAGER_EMAIL] if manager[LINE_MANAGER_EMAIL] else None for manager in data])).all()
        managers = {manager.email: manager.id for manager in managers}
        staff_update_mappings = []

        data_staff_managers = {staff[2]: staff[LINE_MANAGER_EMAIL] for staff in list(
            filter(lambda staff: staff[LINE_MANAGER_EMAIL] != '', data))}

        for staff in staff_list_mappings:
            if staff.email in data_staff_managers:
                staff_update_mappings.append({
                    'id': staff.id,
                    'manager_id': managers[data_staff_managers[staff.email]]
                })
        db.session.bulk_update_mappings(Staff, staff_update_mappings)
        db.session.flush()

        # 4. Add staff to department
        insert_department_staff_mappings = [DepartmentStaff(
            department_id=staff[4],
            staff_id=id_staff_mappings[staff[2]],
            role_title_id=self.get_role_title_id_with_role_title_name(
                department_id=staff[DEPARTMENT_ID], role_title_name=staff[TITLE_NAME].strip())
        ) for staff in data]
        db.session.bulk_save_objects(insert_department_staff_mappings)

        # 5. Add staff to team
        insert_staff_team_mappings = []
        for staff_row in data:
            team_list_data = [item.strip() for item in staff_row[TEAM_NAME].split(
                ',') if item.strip() != '']
            for team_data in team_list_data:
                insert_staff_team_mappings.append({
                    'team_id': self.get_team_id_with_name(name=team_data, company_id=company_id),
                    'staff_id': id_staff_mappings[staff_row[2]]
                })
        db.session.bulk_insert_mappings(StaffTeam, insert_staff_team_mappings)
        return
