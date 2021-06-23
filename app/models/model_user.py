from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.models.model_base import BareBaseModel


class User(BareBaseModel):
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    role = Column(String, default='guest')
    last_login = Column(DateTime)
    manager_id = Column(Integer, ForeignKey("user.id"))

    manager = relationship('User', remote_side='User.id')
