from typing import Optional
from pydantic import BaseModel


from app.helpers.paging import PaginationParams


class ClinicCreate(BaseModel):
    name: str


class ClinicListRequest(PaginationParams):
    search: Optional[str]


class ClinicItemResponse(BaseModel):
    name: str