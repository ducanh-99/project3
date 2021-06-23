from sqlalchemy import Column, String, Text

from app.models.model_base import BareBaseModel


class Company(BareBaseModel):
    company_code = Column(String, index=True, unique=True, comment='ma cong ty')
    company_name = Column(String, index=True, comment='ten cong ty')
    description = Column(Text, nullable=True, comment='mo ta')
