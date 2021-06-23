import jwt

from typing import Optional, List
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from fastapi_sqlalchemy import db
from pydantic import ValidationError, parse_obj_as
from sqlalchemy import asc
from starlette import status

from app.models import User
from app.core.config import settings
from app.core.security import verify_password, get_password_hash
from app.schemas.sche_token import TokenPayload
from app.schemas.sche_user import UserCreateRequest, UserUpdateMeRequest, UserUpdateRequest, UserRegisterRequest, \
    UserTreeResponse
from app.helpers.exception_handler import CustomException
from app.core import error_code, message

class UserService(object):
    __instance = None

    reusable_oauth2 = HTTPBearer(
        scheme_name='Authorization'
    )

    @staticmethod
    def authenticate(*, email: str, password: str) -> Optional[User]:
        """
        Check username and password is correct.
        Return object User if correct, else return None
        """
        user = db.session.query(User).filter_by(email=email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def get_current_user(http_authorization_credentials=Depends(reusable_oauth2)) -> User:
        """
        Decode JWT token to get user_id => return User info from DB query
        """
        try:
            payload = jwt.decode(
                http_authorization_credentials.credentials, settings.SECRET_KEY,
                algorithms=[settings.SECURITY_ALGORITHM]
            )
            token_data = TokenPayload(**payload)
        except(jwt.PyJWTError, ValidationError):
            raise CustomException(http_code=400, code=error_code.ERROR_040_UNAUTHORIZED, message=message.MESSAGE_040_UNAUTHORIZED)
        user = db.session.query(User).get(token_data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    def register_user(data: UserRegisterRequest):
        register_user = User(
            full_name=data.full_name,
            email=data.email,
            hashed_password=get_password_hash(data.password),
            is_active=True,
            role=data.role.value,
        )
        db.session.add(register_user)
        db.session.commit()
        return register_user

    @staticmethod
    def create_user(data: UserCreateRequest):
        new_user = User(
            full_name=data.full_name,
            email=data.email,
            hashed_password=get_password_hash(data.password),
            is_active=data.is_active,
            role=data.role.value,
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def update_me(data: UserUpdateMeRequest, current_user: User):
        current_user.full_name = current_user.full_name if data.full_name is None else data.full_name
        current_user.email = current_user.email if data.email is None else data.email
        current_user.hashed_password = current_user.hashed_password if data.password is None else get_password_hash(
            data.password)
        db.session.commit()
        return current_user

    @staticmethod
    def update(user: User, data: UserUpdateRequest):
        user.full_name = user.full_name if data.full_name is None else data.full_name
        user.email = user.email if data.email is None else data.email
        user.hashed_password = user.hashed_password if data.password is None else get_password_hash(
            data.password)
        user.is_active = user.is_active if data.is_active is None else data.is_active
        user.role = user.role if data.role is None else data.role.value
        db.session.commit()
        return user

    @classmethod
    def get_child(self):
        users = db.session.query(User).order_by(asc(User.id)).all()
        return self.format_staff_tree(users, None)

    @staticmethod
    def format_staff_tree(staff_dbs: List[User], root_id: Optional[int]):
        map_staff = {}
        staffs = []
        root = []
        i = 0

        # init map staff
        for staff in staff_dbs:
            staffs.append(parse_obj_as(UserTreeResponse, staff))
            map_staff[staff.id] = i
            i += 1

        for staff in staffs:
            # Get staff tree of 1 staff
            if root_id is not None:
                if staff.id != root_id:
                    staffs[map_staff[staff.parent_id]].children.append(staff)
                else:
                    root = staff
            # Get staff tree of all staff
            else:
                if staff.parent_id is not None:
                    staffs[map_staff[staff.parent_id]].children.append(staff)
                else:
                    root.append(staff)
        return root
