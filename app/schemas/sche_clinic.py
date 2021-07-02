from app.services.base_service import BaseService
from typing import Optional
from pydantic import BaseModel


from app.helpers.paging import PaginationParams


class ClinicCreate(BaseModel):
    name: str


class ClinicListRequest(PaginationParams):
    search: Optional[str]


class ClinicItemResponse(BaseService):
    name: str