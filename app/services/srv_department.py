from typing import Any, List

from sqlalchemy.sql import func
from fastapi_sqlalchemy import db
from app.helpers.exception_handler import CustomException
from app.helpers.paging import paginate, Page
from app.models import Department, Company, DepartmentStaff, Staff, RoleTitle, CompanyStaff, StaffTeam, Team
from app.schemas.sche_department import DepartmentCreateRequest, DepartmentListRequest, DepartmentItemResponse, \
    DepartmentAddStaffRequest, DepartmentUpdateStaffRequest
from app.core import error_code, message
from app.services.srv_base import BaseService


class DepartmentService(BaseService):
    list_children = []

    def __init__(self):
        super().__init__(Department)

    def get_query_by_company(self, company_id: int):
        _query = db.session.query(self.model).filter(self.model.company_id == company_id)
        return _query

    def get_query_all_departments(self, company_id: int):
        _query = self.get_query_by_company(company_id=company_id)
        _query = _query.join(DepartmentStaff, DepartmentStaff.department_id == self.model.id, isouter=True) \
            .with_entities(
            self.model.id,
            self.model.department_name,
            self.model.description,
            self.model.parent_id,
            self.model.created_at,
            self.model.updated_at,
            func.count(DepartmentStaff.staff_id).filter(DepartmentStaff.is_active).label('count_staffs')
        ).group_by(self.model.id)
        return _query

    def get_list_with_paging(self, department_list_req: DepartmentListRequest) -> Page[DepartmentItemResponse]:
        _query = self.get_query_all_departments(company_id=department_list_req.company_id)
        _query = _query.filter(self.model.is_active)
        if department_list_req.department_name:
            _query = _query.filter(self.model.department_name.ilike(f'%{department_list_req.department_name}%'))
        if department_list_req.parent_id:
            _query = _query.filter(self.model.parent_id == department_list_req.parent_id)

        departments = paginate(model=self.model, query=_query, params=department_list_req)

        return departments

    def get_tree(self, company_id: int):
        _query = self.get_query_all_departments(company_id=company_id)
        _query = _query.filter(self.model.is_active)
        all_departments = _query.all()
        all_departments = [dict(department) for department in all_departments]
        root_departments = list(filter(lambda department: not department['parent_id'], all_departments))
        # root_departments = [{
        #     'department': root_department,
        #     'children': self.get_children_with_staff_code(node_department=root_department, all_departments=all_departments)
        # } for root_department in root_departments]
        for index, root_department in enumerate(root_departments):
            count_staff = root_department['count_staffs']
            my_children, staff_children = self.get_children_with_staff_code(node_department=root_department, all_departments=all_departments)
            my_dict = {
                'department': root_department,
                'children': my_children
            }
            root_departments[index] = my_dict
            count_staff += staff_children

        return root_departments

    def get_children(self, node_department: Department, all_departments: List[Department]):
        """
        get children with tree
        """
        children = list(filter(lambda department: department.parent_id == node_department.id, all_departments))
        children = [{
            'department': child,
            'children': self.get_children(node_department=child, all_departments=all_departments)
        } for child in children]

        return children

    def get_children_with_staff_code(self, node_department: Department, all_departments: List[Department]):
        """
        get children with tree
        """
        children = list(filter(lambda department: department['parent_id'] == node_department['id'], all_departments))
        count_staff = node_department['count_staffs']
        for index, child in enumerate(children):
            my_children, staff_children = self.get_children_with_staff_code(node_department=child, all_departments=all_departments)
            my_dict = {
                'department': child,
                'children': my_children
            }
            children[index] = my_dict
            count_staff += staff_children
        node_department['count_staffs'] = count_staff
        return children, count_staff

    def get_list_children(self, node_department: Department, all_departments: List[Department]):
        children = list(filter(lambda department: department.parent_id == node_department.id, all_departments))
        for child in children:
            self.list_children.append(child)
            self.get_list_children(node_department=child, all_departments=all_departments)

    def get_list_children_return(self, node_department: Department, all_departments: List[Department]) -> List:
        list_children = []

        def recursion(node_department: Department, all_departments: List[Department]):
            nonlocal list_children
            children = list(
                filter(lambda department: department.parent_id == node_department.id, all_departments))
            for child in children:
                list_children.append(child)
                recursion(node_department=child, all_departments=all_departments)

        recursion(node_department=node_department, all_departments=all_departments)
        return list_children
    
    @staticmethod
    def add_list_team(all_staffs):
        all_staffs = [staff._asdict() for staff in all_staffs]
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
    
    def get_detail(self, id: int):
        department = db.session.query(self.model).get(id)
        if not department:
            raise CustomException(http_code=400, code=error_code.ERROR_091_DEPARTMENT_ID_NOT_EXISTS,
                                  message=message.MESSAGE_091_DEPARTMENT_ID_NOT_EXISTS)

        department_data = department.__dict__

        if department.parent_id:
            department_data['parent'] = {
                'id': department.parent_id,
                'department_name': department.parent.department_name
            }

        department_data['company'] = {
            'id': department.company_id,
            'company_code': department.company.company_code,
            'company_name': department.company.company_name
        }
        # staffs = self.get_staffs(department_id=department.id)
        # department_data['count_staffs'] = staffs['count']
        # department_data['staff'] = [staff for staff in staffs['data']]

        all_departments = self.get_query_all_departments(company_id=department.company_id).all()
        list_children = self.get_list_children_return(node_department=department, all_departments=all_departments)
        list_children.append(department)
        department_data['staff'] = []
        for child in list_children:
            staffs = self.get_staffs(department_id=child.id)
            department_data['staff'].extend(staffs['data'])
        department_data['count_staffs'] = len(department_data['staff'])
        department_data['staff'] = self.add_list_team(all_staffs=department_data['staff'])
        department_data['children'] = self.get_children(node_department=department, all_departments=all_departments)

        return department_data

    @staticmethod
    def get_staffs(department_id: int):
        staffs = db.session.query(Staff) \
            .join(DepartmentStaff, DepartmentStaff.staff_id == Staff.id, isouter=True)\
            .filter(DepartmentStaff.department_id == department_id, DepartmentStaff.is_active == True) \
            .filter(Staff.is_active) \
            .with_entities(
            Staff.id,
            Staff.full_name,
            Staff.staff_code,
            Staff.email,
            Staff.phone_number)
        return {'count': staffs.count(), 'data': staffs.all()}

    def get_detail_with_tree(self, id: int, company: Company):
        department = db.session.query(self.model).filter(self.model.id == id,
                                                         self.model.company_id == company.id).first()
        if not department:
            raise CustomException(http_code=400, code=error_code.ERROR_091_DEPARTMENT_ID_NOT_EXISTS,
                                  message=message.MESSAGE_091_DEPARTMENT_ID_NOT_EXISTS)

        all_departments = db.session.query(self.model).filter(self.model.company_id == company.id).with_entities(
            self.model.id,
            self.model.name,
            self.model.description,
            self.model.parent_id
        ).all()

        return {'department': department,
                'children': self.get_children(node_department=department, all_departments=all_departments)}

    def create_or_update(self, req_data: DepartmentCreateRequest):
        company = db.session.query(Company).get(req_data.company_id)
        if not company:
            raise CustomException(http_code=400, code=error_code.ERROR_061_COMPANY_NOT_FOUND,
                                  message=message.MESSAGE_061_COMPANY_NOT_FOUND)

        if req_data.parent_id:
            parent_department = db.session.query(self.model).get(req_data.parent_id)
            if not parent_department:
                raise CustomException(http_code=400, code=error_code.ERROR_094_DEPARTMENT_PARENT_NOT_EXISTS,
                                      message=message.MESSAGE_094_DEPARTMENT_PARENT_NOT_EXISTS)

            if parent_department.company_id != company.id:
                raise CustomException(http_code=400, code=error_code.ERROR_103_PARENT_DEPARTMENT_NOT_BELONG_TO_COMPANY,
                                      message=message.MESSAGE_103_PARENT_DEPARTMENT_NOT_BELONG_TO_COMPANY)

            if not parent_department.is_active:
                raise CustomException(http_code=400, code=error_code.ERROR_104_PARENT_DEPARTMENT_INACTIVE,
                                      message=message.MESSAGE_104_PARENT_DEPARTMENT_INACTIVE)

        if not req_data.id:
            new_department = Department(
                department_name=req_data.department_name,
                description=req_data.description,
                parent_id=req_data.parent_id if req_data.parent_id else None,
                company_id=req_data.company_id
            )
            db.session.add(new_department)
            db.session.commit()

            return new_department
        else:
            exits_department = db.session.query(self.model).get(req_data.id)
            if not exits_department:
                raise CustomException(http_code=400, code=error_code.ERROR_091_DEPARTMENT_ID_NOT_EXISTS,
                                      message=message.MESSAGE_091_DEPARTMENT_ID_NOT_EXISTS)
            if not req_data.is_active:
                if self.get_staffs(exits_department.id)['count'] > 0:
                    raise CustomException(http_code=400,
                                          code=error_code.ERROR_095_CAN_NOT_DISABLE_DEPARTMENT_HAVE_STAFF,
                                          message=message.MESSAGE_095_CAN_NOT_DISABLE_DEPARTMENT_HAVE_STAFF)

            if req_data.id == req_data.parent_id:
                raise CustomException(http_code=400, 
                                      code=error_code.ERROR_108_PARENT_NOT_YOURSELF,
                                      message=message.MESSAGE_108_PARENT_NOT_YOURSELF)
            self.list_children = []
            all_departments = self.get_query_all_departments(company_id=exits_department.company_id).all()
            self.get_list_children(node_department=exits_department, all_departments=all_departments)
            if req_data.parent_id in [child.id for child in self.list_children]:
                raise CustomException(http_code=400,
                                      code=error_code.ERROR_099_PARENT_ID_BELONG_TO_CHILD_DEPARTMENT,
                                      message=message.MESSAGE_099_PARENT_ID_BELONG_TO_CHILD_DEPARTMENT)
            if not req_data.is_active:
                for child in self.list_children:
                    if child.count_staffs > 0:
                        raise CustomException(http_code=400,
                                              code=error_code.ERROR_096_CAN_NOT_DISABLE_DEPARTMENT_WHEN_CHILD_HAVE_STAFF,
                                              message=message.MESSAGE_096_CAN_NOT_DISABLE_DEPARTMENT_WHEN_CHILD_HAVE_STAFF)

            if exits_department.company_id != req_data.company_id:
                raise CustomException(http_code=400,
                                      code=error_code.ERROR_100_CAN_NOT_UPDATE_DEPARTMENT_COMPANY,
                                      message=message.MESSAGE_100_CAN_NOT_UPDATE_DEPARTMENT_COMPANY)

            exits_department.department_name = req_data.department_name
            exits_department.description = req_data.description
            exits_department.parent_id = req_data.parent_id
            exits_department.department_name = req_data.department_name
            exits_department.is_active = req_data.is_active

            if not req_data.is_active:
                # Khoa toan bo role_title truc thuoc
                db.session.query(RoleTitle).filter(RoleTitle.department_id == exits_department.id).update(
                    {"is_active": False})
                # Khoa toan bo child department
                department_ids = [child.id for child in self.list_children]
                department_ids.append(req_data.id)
                if not self.lock_list_departments_action(department_ids=department_ids):
                    raise CustomException(http_code=400,
                                          code=error_code.ERROR_096_CAN_NOT_DISABLE_DEPARTMENT_WHEN_CHILD_HAVE_STAFF,
                                          message=message.MESSAGE_096_CAN_NOT_DISABLE_DEPARTMENT_WHEN_CHILD_HAVE_STAFF)

            db.session.commit()
            return exits_department

    @staticmethod
    def lock_list_departments_action(department_ids: list):
        department_staffs = db.session.query(DepartmentStaff).filter(
            DepartmentStaff.department_id.in_(department_ids)).all()
        for department_staff in department_staffs:
            if department_staff.is_active:
                return False
        # Lock all Department_Staff
        db.session.query(DepartmentStaff).filter(DepartmentStaff.department_id.in_(department_ids)).update(
            {"is_active": False})
        # Lock all Role Title thuoc ve list department
        db.session.query(RoleTitle).filter(RoleTitle.department_id.in_(department_ids)).update(
            {"is_active": False})
        # Lock all list Department
        db.session.query(Department).filter(Department.id.in_(department_ids)).update({"is_active": False})
        return True

    def add_staff(self, req_data: DepartmentAddStaffRequest):
        department = db.session.query(self.model).get(req_data.department_id)
        if not department:
            raise CustomException(http_code=400, code=error_code.ERROR_091_DEPARTMENT_ID_NOT_EXISTS,
                                  message=message.MESSAGE_091_DEPARTMENT_ID_NOT_EXISTS)
        if not department.is_active:
            raise CustomException(http_code=400, code=error_code.ERROR_107_DEPARTMENT_INACTIVE,
                                  message=message.MESSAGE_107_DEPARTMENT_INACTIVE)
        staff_ids = [staff.staff_id for staff in req_data.staffs]
        self.validate_list_staffs(department=department, staff_ids=staff_ids)

        staff_other_dept = self.get_staffs_in_other_department(department=department, staff_ids=staff_ids)
        if len(staff_other_dept) > 0:
            raise CustomException(
                http_code=400,
                code=error_code.ERROR_105_STAFF_BELONG_TO_OTHER_DEPARTMENT,
                message=message.MESSAGE_105_STAFF_BELONG_TO_OTHER_DEPARTMENT + str(
                    [so.staff_id for so in staff_other_dept])
            )

        role_title_ids = [staff.role_title_id for staff in req_data.staffs]
        self.validate_list_role_title(department=department, role_title_ids=role_title_ids)

        self.add_staff_action(department_id=department.id, staffs=req_data.staffs)

        db.session.flush()
        db.session.commit()
        return

    def add_staff_action(self, department_id: int, staffs: list):
        staff_ids = [staff.staff_id for staff in staffs]

        # Update exist department_staffs
        update_department_staffs = db.session.query(DepartmentStaff).filter(
            DepartmentStaff.department_id == department_id, DepartmentStaff.staff_id.in_(staff_ids)).all()
        update_department_staffs_mappings = [{
            'id': update_department_staff.id,
            'is_active': True
        } for update_department_staff in update_department_staffs]
        db.session.bulk_update_mappings(DepartmentStaff, update_department_staffs_mappings)

        # Insert new department_staffs
        insert_department_staff_mappings = []
        for staff in staffs:
            if staff.staff_id not in [update_department_staff.staff_id for update_department_staff in
                                      update_department_staffs]:
                insert_department_staff_mappings.append({
                    'department_id': department_id,
                    'staff_id': staff.staff_id,
                    'role_title_id': staff.role_title_id,
                    'is_active': True
                })
        db.session.bulk_insert_mappings(DepartmentStaff, insert_department_staff_mappings)

        return

    @staticmethod
    def validate_list_staffs(department: Department, staff_ids: list):
        staffs = db.session.query(Staff).filter(Staff.id.in_(staff_ids)).all()
        if len(staffs) != len(set(staff_ids)):
            raise CustomException(http_code=400, code=error_code.ERROR_134_STAFF_ID_NOT_FOUND,
                                  message=message.MESSAGE_134_STAFF_ID_NOT_FOUND)
        for staff in staffs:
            if not staff.is_active:
                raise CustomException(http_code=400, code=error_code.ERROR_106_STAFF_INACTIVE,
                                      message=message.MESSAGE_106_STAFF_INACTIVE + str(staff.id))

        company_staffs = db.session.query(CompanyStaff).filter(
            CompanyStaff.staff_id.in_(staff_ids),
            CompanyStaff.company_id == department.company_id,
            CompanyStaff.is_active == True
        ).all()
        if len(company_staffs) != len(set(staff_ids)):
            raise CustomException(http_code=400, code=error_code.ERROR_097_STAFF_AND_DEPARTMENT_NOT_SAME_COMPANY,
                                  message=message.MESSAGE_097_STAFF_AND_DEPARTMENT_NOT_SAME_COMPANY)
        return

    @staticmethod
    def validate_list_role_title(department: Department, role_title_ids: list):
        role_titles = db.session.query(RoleTitle).filter(
            RoleTitle.id.in_(role_title_ids)).all()
        if len(role_titles) != len(set(role_title_ids)):
            raise CustomException(http_code=400, code=error_code.ERROR_191_ROLE_ID_DOES_NOT_EXITS,
                                  message=message.MESSAGE_191_ROLE_ID_DOES_NOT_EXITS)
        for role_title in role_titles:
            if role_title.department_id != department.id:
                raise CustomException(http_code=400, code=error_code.ERROR_098_ROLE_TITLE_NOT_BELONG_TO_DEPARTMENT,
                                      message=message.MESSAGE_098_ROLE_TITLE_NOT_BELONG_TO_DEPARTMENT)
            if not role_title.is_active:
                raise CustomException(http_code=400, code=error_code.ERROR_101_ROLE_TITLE_DELETED,
                                      message=message.MESSAGE_101_ROLE_TITLE_DELETED)
        return

    @staticmethod
    def get_staffs_in_other_department(department: Department, staff_ids: list):
        # check staff da thuoc department khac chua
        other_department_in_company = db.session.query(Department).filter(
            Department.company_id == department.company_id,
            Department.id != department.id,
            Department.is_active == True
        ).all()

        staff_other_dept = db.session.query(DepartmentStaff).filter(
            DepartmentStaff.staff_id.in_(staff_ids),
            DepartmentStaff.department_id.in_(
                [other_department.id for other_department in other_department_in_company]),
            DepartmentStaff.is_active == True
        ).all()
        return staff_other_dept

    def create_or_update_staff(self, req_data: DepartmentUpdateStaffRequest):
        department = db.session.query(self.model).get(req_data.department_id)
        if not department:
            raise CustomException(http_code=400, code=error_code.ERROR_091_DEPARTMENT_ID_NOT_EXISTS,
                                  message=message.MESSAGE_091_DEPARTMENT_ID_NOT_EXISTS)
        company_id = department.company_id

        self.validate_list_staffs(department=department, staff_ids=[req_data.staff_id])
        self.validate_list_role_title(department=department, role_title_ids=[req_data.role_title_id])

        depart_in_com = db.session.query(self.model).filter(
            self.model.company_id == company_id,
            self.model.is_active == True
        ).all()

        exists_department_staffs = db.session.query(DepartmentStaff).filter(
            DepartmentStaff.department_id.in_([depart.id for depart in depart_in_com]),
            DepartmentStaff.staff_id == req_data.staff_id,
        ).all()

        if len(exists_department_staffs) == 0:
            # Trong 1 công ty. nếu Staff chưa thuộc Department nào thì tạo mới Department-Staff
            new_department_staff = DepartmentStaff(
                department_id=department.id,
                staff_id=req_data.staff_id,
                role_title_id=req_data.role_title_id,
                is_active=req_data.is_active
            )
            db.session.add(new_department_staff)
            db.session.commit()
            return
        else:
            # Trong 1 công ty. nếu Staff đã thuộc Department (bất kể trạng thái)
            department_staff_active = None
            for exists_department_staff in exists_department_staffs:
                if exists_department_staff.is_active:
                    department_staff_active = exists_department_staff
                    break
            if department_staff_active:  # Trong 1 công ty, nếu Staff đang thuộc 1 Department
                if department_staff_active.department_id != department.id:
                    # Nếu Department truyền lên khác Department đã có => raise lỗi
                    raise CustomException(
                        http_code=400,
                        code=error_code.ERROR_105_STAFF_BELONG_TO_OTHER_DEPARTMENT,
                        message=message.MESSAGE_105_STAFF_BELONG_TO_OTHER_DEPARTMENT + str(req_data.staff_id)
                    )
                else:
                    # Nếu Department truyền lên trùng Department đã có => Update
                    department_staff_active.role_title_id = req_data.role_title_id if req_data.role_title_id else department_staff_active.role_title_id
                    department_staff_active.is_active = req_data.is_active if req_data.is_active is not None else department_staff_active.is_active
                    db.session.commit()
                    return
            else:  # Trong 1 công ty, nếu Staff không thuộc Department nào (tất cả Department-Staff đang inactive)
                department_staff_inactive = None
                for exists_department_staff in exists_department_staffs:
                    if not exists_department_staff.is_active and exists_department_staff.department_id == department.id:
                        department_staff_inactive = exists_department_staff
                        break
                if department_staff_inactive is None:  # Department ko trùng với Department-Staff đã có => create
                    new_department_staff = DepartmentStaff(
                        department_id=department.id,
                        staff_id=req_data.staff_id,
                        role_title_id=req_data.role_title_id,
                        is_active=req_data.is_active
                    )
                    db.session.add(new_department_staff)
                    db.session.commit()
                    return
                else:  # Department trùng với Department-Staff đã có => update
                    department_staff_inactive.role_title_id = req_data.role_title_id if req_data.role_title_id else department_staff_inactive.role_title_id
                    department_staff_inactive.is_active = req_data.is_active if req_data.is_active is not None else department_staff_inactive.is_active
                    db.session.commit()
                    return
