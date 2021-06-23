# Import all the models, so that Base has them before being
# imported by Alembic
from app.models.model_base import Base  # noqa
from app.models.model_user import User  # noqa
from app.models.model_company import Company
from app.models.model_department import Department
from app.models.model_role_title import RoleTitle
from app.models.model_team import Team
from app.models.model_staff import Staff
from app.models.model_staff_team import StaffTeam
from app.models.model_company_staff import CompanyStaff
from app.models.model_department_staff import DepartmentStaff
