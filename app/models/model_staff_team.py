from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from .model_base import BareBaseModel


class StaffTeam(BareBaseModel):
    __tablename__ = 'staff_team'
    staff_id = Column(Integer, ForeignKey('staff.id'))
    team_id = Column(Integer, ForeignKey('team.id'))
    is_active = Column(Boolean, default=True)

    staff = relationship('Staff', remote_side='Staff.id')
    team = relationship('Team', remote_side='Team.id')

    __table_args__ = (
        UniqueConstraint('staff_id', 'team_id', name='_staff_team_unique'),
    )
