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
