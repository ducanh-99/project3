from fastapi import APIRouter

from app.api.base import api_healthcheck, api_company, api_department, api_role_title, api_common, api_staff, api_team

router = APIRouter()

router.include_router(api_healthcheck.router, tags=["healthcheck"], prefix="/healthcheck")
router.include_router(api_common.router, tags=["common"], prefix="/common")
router.include_router(api_company.router, tags=["company"], prefix="/companies")
router.include_router(api_department.router, tags=["department"], prefix="/departments")
router.include_router(api_role_title.router, tags=["role_title"], prefix="/role_titles")
router.include_router(api_team.router, tags=["teams"], prefix="/teams")
router.include_router(api_staff.router, tags=["staffs"], prefix="/staffs")
