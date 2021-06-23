from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.models.model_base import BareBaseModel


class Team(BareBaseModel):
    team_name = Column(String(255), index=True, comment='ten team')
    description = Column(Text, nullable=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company_branch = Column(String(255), nullable=True, comment='ten chi nhanh')
    is_active = Column(Boolean, default=True)

    company = relationship('Company', remote_side='Company.id')
    