from typing import List, Optional
from pydantic import BaseModel


from app.helpers.paging import PaginationParams


class ClinicCreate(BaseModel):
    name: str


class ClinicListRequest(PaginationParams):
    search: Optional[str]


class ClinicItemResponse(BaseModel):
    name: str


class ClinicDetail(BaseModel):
    class Patient(BaseModel):
        class Config:
            orm_mode = True
        id: int
        name: str
        age: int
        diagnostic: str

    class Config:
        orm_mode = True

    name: str
    patients: Optional[List[Patient]] = []
