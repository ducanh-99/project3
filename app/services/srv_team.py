
from typing import List, Optional

from fastapi_sqlalchemy import db
from sqlalchemy.orm import query
from sqlalchemy.sql.elements import or_

from app.schemas.sche_staff import StaffList, StaffRequest, StaffsRequest
from app.models import StaffTeam, Company, Team, Staff, DepartmentStaff, Department
from app.helpers.exception_handler import CustomException
from app.schemas.sche_team import TeamCreateRequest, TeamDetailResponse, TeamItemResponse, TeamListRequest, TeamUpdateRequest
from app.helpers.paging import paginate, Page
from app.core import error_code, message
from app.services.srv_base import BaseService


class TeamService(BaseService):
    def __init__(self):
        super().__init__(Team)

    def create(self, data: TeamCreateRequest):
        self._validate_common(team=data, company_id=data.company_id)
        if data.team_name:
            exist_team = db.session.query(self.model).filter(
                self.model.team_name == data.team_name,
                self.model.company_id == data.company_id,
                self.model.is_active
            ).first()

            if exist_team:
                raise CustomException(http_code=400,
                                      code=error_code.ERROR_160_EXISTS_TEAM, message=message.MESSAGE_160_EXISTS_TEAM)
        new_team = Team(
            team_name=data.team_name,
            description=data.description,
            company_id=data.company_id,
            is_active=data.is_active
        )
        db.session.add(new_team)
        db.session.commit()
        return new_team

    def _get_team(self, id: Optional[int]):
        exist_team = db.session.query(self.model).filter(
            self.model.id == id,
        ).first()
        return exist_team

    def _get_teams(self, staff_id: int) -> List[StaffTeam]:
        exist_teams = db.session.query(StaffTeam).filter(
            StaffTeam.staff_id == staff_id).all()
        return exist_teams

    def _check_exists_team(self, id: int):
        exist_team = self._get_team(id=id)
        if not exist_team or not exist_team.is_active:
            raise CustomException(
                http_code=400,
                code=error_code.ERROR_161_TEAM_ID_NOT_FOUND,
                message=message.MESSAGE_161_TEAM_ID_NOT_FOUND
            )
        return exist_team

    def _get_staffs_in_team(self, team_id):
        join_table = db.session.query(Staff).join(
            StaffTeam).filter(StaffTeam.team_id == team_id, StaffTeam.is_active).all()
        return join_table

    def _get_staff_in_team(self, team_id, staff_id):
        staff = db.session.query(StaffTeam).filter(
            StaffTeam.team_id == team_id, StaffTeam.staff_id == staff_id).first()

        return staff

    @staticmethod
    def _get_staff_team_by_id_staff_and_team(team_id, staff_id):
        staff_team = db.session.query(StaffTeam).filter(
            StaffTeam.team_id == team_id, StaffTeam.staff_id == staff_id).first()
        return staff_team

    def _get_department_name(self, staffs: List):
        if staffs == None:
            return
        query = db.session.query(Department).join(DepartmentStaff)
        for index, staff in enumerate(staffs):
            department = query.filter(
                DepartmentStaff.staff_id == staff["id"], DepartmentStaff.is_active).first()
            staff["department"] = department.department_name if department else None
            staffs[index] = staff
        return staffs

    def get_detail(self, id: Optional[int]) -> TeamDetailResponse:
        team = self._get_team(id)
        if not team:
            raise CustomException(
                http_code=400,
                code=error_code.ERROR_161_TEAM_ID_NOT_FOUND,
                message=message.MESSAGE_161_TEAM_ID_NOT_FOUND
            )
        staffs = self._get_staffs_in_team(team_id=id)
        # covert staffs to dictionary
        for i in range(len(staffs)):
            staffs[i] = staffs[i].__dict__
        staffs = self._get_department_name(staffs=staffs)
        response = TeamDetailResponse(
            id=team.id,
            team_name=team.team_name,
            description=team.description,
            staffs=staffs,
            count_staff=len(staffs),
            created_at=team.created_at,
            updated_at=team.updated_at
        ).dict(exclude_none=True)
        return response

    def get_list_with_paging(self, team_list_req: TeamListRequest) -> Page[TeamItemResponse]:
        company_exists = db.session.query(Company).filter(
            Company.id == team_list_req.company_id).first()
        if not company_exists:
            raise CustomException(http_code=400, code=error_code.ERROR_061_COMPANY_NOT_FOUND,
                                  message=message.MESSAGE_061_COMPANY_NOT_FOUND)
        _query = db.session.query(self.model).filter(
            self.model.company_id == team_list_req.company_id, self.model.is_active == True)
        if team_list_req.search:
            value = team_list_req.search
            _query = _query.filter(
                or_(
                    self.model.team_name.ilike('%' + value + '%'),
                    self.model.description.ilike('%' + value + '%'))
            )
        teams = paginate(model=self.model, query=_query, params=team_list_req)

        # add count_staff
        data_teams = [data.__dict__ for data in teams.data]
        for i in range(len(data_teams)):
            team_id = data_teams[i]['id']
            data_teams[i]['count_staff'] = len(
                self._get_staffs_in_team(team_id=team_id))
        teams.data = data_teams

        return teams

    def get_staff_by_id(self, staff_id):
        staff_exists = db.session.query(Staff).filter(
            Staff.id == staff_id).first()
        return staff_exists

    def _check_staffs_exists(self, staffs):
        for staff in staffs:
            exist_staff = self.get_staff_by_id(staff_id=staff.id)
            if not exist_staff:
                raise CustomException(
                    code=error_code.ERROR_134_STAFF_ID_NOT_FOUND,
                    message=message.MESSAGE_134_STAFF_ID_NOT_FOUND
                )

    def _remove_staffs_in_team(self, staffs, team_id) -> List:
        remove_index = []
        for index, staff in enumerate(staffs):
            staff_team = db.session.query(StaffTeam).filter(
                StaffTeam.team_id == team_id,
                StaffTeam.staff_id == staff.id
            ).first()
            if staff_team:
                staff_team.is_active = True
                remove_index.append(index)
        for index in remove_index:
            staffs.pop(index)
        return staffs

    def _get_company_id(self, team_id):
        team = self._get_team(id=team_id)
        return team.company_id

    def _check_staff_and_team_not_in_company(self, team_id, staffs=[], staff_id=None):
        company_id = self._get_company_id(team_id=team_id)
        if staff_id:
            company = db.session.query(Staff).filter(Staff.id == staff_id,
                                                     Staff.company_id == company_id).first()
            if not company:
                raise CustomException(http_code=400, code=error_code.ERROR_162_STAFF_AND_TEAM_NOT_BELONG_SAME_COMPANY,
                                      message=message.MESSAGE_162_STAFF_AND_TEAM_NOT_BELONG_SAME_COMPANY)
        for staff in staffs:
            company = db.session.query(Staff).filter(Staff.id == staff.id,
                                                     Staff.company_id == company_id).first()
            if not company:
                raise CustomException(http_code=400, code=error_code.ERROR_162_STAFF_AND_TEAM_NOT_BELONG_SAME_COMPANY,
                                      message=message.MESSAGE_162_STAFF_AND_TEAM_NOT_BELONG_SAME_COMPANY)

    def add_staffs(self, data: StaffList):
        if data.team_id:
            self._check_exists_team(id=data.team_id)

        self._check_staffs_exists(staffs=data.staffs)
        self._check_staff_and_team_not_in_company(
            team_id=data.team_id, staffs=data.staffs)
        data.staffs = self._remove_staffs_in_team(
            staffs=data.staffs, team_id=data.team_id)
        staff_team = []
        for staff in data.staffs:
            staff_team.append(
                StaffTeam(
                    team_id=data.team_id,
                    staff_id=staff.id,
                )
            )
        db.session.add_all(staff_team)
        db.session.commit()

    def _validate_common(self, team, company_id: int):
        # Note manger_id if exists
        # if data.manager_id or data.manager_id == 0:
        #     manager = db.session.query(Staff).filter(
        #         Staff.id == data.manager_id).first()
        #     if not manager:
        #         raise CustomException(http_code=400, code=error_code.ERROR_130_MANAGER_NOT_FOUND,
        #                               message=message.MESSAGE_130_MANAGER_NOT_FOUND)
        #     manager = db.session.query(Staff).filter(
        #         Staff.id == data.manager_id, Staff.id == company_id).first()
        #     if not manager:
        #         raise CustomException(http_code=400, code=error_code.ERROR_129_MANAGER_ID_INVALID,
        #                               message=message.MESSAGE_129_MANAGER_ID_INVALID)
        company = db.session.query(Company).filter(
            Company.id == company_id).first()
        if not company:
            raise CustomException(http_code=400, code=error_code.ERROR_061_COMPANY_NOT_FOUND,
                                  message=message.MESSAGE_061_COMPANY_NOT_FOUND)

    def update(self, id: int, data: TeamUpdateRequest):
        team = self._check_exists_team(id=id)

        self._validate_common(team=data, company_id=team.company_id)
        if data.team_name:
            exist_team = db.session.query(self.model).filter(self.model.team_name == data.team_name,
                                                             self.model.company_id == team.company_id,
                                                             self.model.is_active,
                                                             self.model.id != id).first()
            if exist_team:
                raise CustomException(http_code=400, code=error_code.ERROR_160_EXISTS_TEAM,
                                      message=message.MESSAGE_160_EXISTS_TEAM)
        if data.is_active == False:
            staffs = self._get_staffs_in_team(team_id=id)
            if len(staffs) > 0:
                raise CustomException(http_code=400, code=error_code.ERROR_164_CANNOT_DELETE_TEAM,
                                      message=message.MESSAGE_164_CANNOT_DELETE_TEAM)
        team.team_name = data.team_name if data.team_name else team.team_name
        team.description = data.description if data.description else team.description
        team.is_active = data.is_active if data.is_active is not None else team.is_active
        db.session.commit()
        return team

    def update_staff(self, data: StaffRequest):
        self._check_exists_team(id=data.team_id)
        self._check_staff_and_team_not_in_company(
            team_id=data.team_id, staff_id=data.staff_id)
        staff = self._get_staff_in_team(
            team_id=data.team_id, staff_id=data.staff_id)
        is_create = False
        if not staff:
            is_create = True
            staff = StaffTeam()
        staff.team_id = data.team_id if data.team_id else staff.team_id
        staff.staff_id = data.staff_id if data.staff_id else staff.staff_id
        # is_active == Flase is not change value is_active
        staff.is_active = data.is_active if data.is_active or data.is_active == False else staff.is_active
        if is_create:
            db.session.add(staff)
        db.session.commit()

    def add_staff_to_teams(self, staff_id: int, teams: List):
        if teams == None:
            return
        for team in teams:
            self._check_exists_team(id=team.team_id)
            self._check_staff_and_team_not_in_company(
                team_id=team.team_id, staff_id=staff_id)
            staff_team = StaffTeam(
                team_id=team.team_id,
                staff_id=staff_id,
                is_active=team.is_active if team.is_active is not None else True
            )
            db.session.add(staff_team)

    def update_staff_to_teams(self, staff_id: int, teams: List):
        if teams == None:
            return
        for team in teams:
            self._check_exists_team(id=team.team_id)
            self._check_staff_and_team_not_in_company(
                team_id=team.team_id, staff_id=staff_id)
            staff_team = self._get_staff_team_by_id_staff_and_team(
                team_id=team.team_id, staff_id=staff_id)
            if staff_team is None:
                staff_team = StaffTeam(
                    team_id=team.team_id,
                    staff_id=staff_id,
                    is_active=team.is_active if team.is_active is not None else True
                )
                db.session.add(staff_team)
            else:
                staff_team.team_id = team.team_id
                staff_team.is_active = team.is_active if team.is_active is not None else True

    def update_staff_in_teams(self, staff_id: int, teams: List):
        all_teams = self._get_teams(staff_id=staff_id)
        if teams == None:
            for team_db in all_teams:
                team_db.is_active = False
            return
        # validate
        for team in teams:
            self._check_exists_team(id=team.team_id)
            self._check_staff_and_team_not_in_company(
                team_id=team.team_id, staff_id=staff_id)
        # active all teams exists
        for team_db in all_teams:
            team_db.is_active = False
            for team in teams:
                if team_db.team_id == team.team_id:
                    team_db.is_active = True
                    teams.remove(team)
        # create new team
        for team in teams:
            staff_team = StaffTeam(
                team_id=team.team_id,
                staff_id=staff_id,
                is_active=team.is_active if team.is_active is not None else True
            )
            db.session.add(staff_team)
