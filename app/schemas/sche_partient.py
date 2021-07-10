from app.helpers.enums import Gender
from typing import List, Optional
from pydantic import BaseModel


class RecommendPatient(BaseModel):

    id: Optional[int]
    name: str
    gender: Gender
    age: int
    diagnostic: str
    disease: Optional[str]


class RecommendResponse(BaseModel):

    class Clinic(BaseModel):
        id: int
        name: str

        class Config:
            orm_mode = True

    total_wait: float
    clinis: List[Clinic]
