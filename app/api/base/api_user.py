import logging
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi_sqlalchemy import db
from pydantic.tools import parse_obj_as
from sqlalchemy import asc

from app.helpers.exception_handler import CustomException
from app.helpers.login_manager import login_required, PermissionRequired
from app.helpers.paging import Page, PaginationParams, paginate
from app.schemas.sche_base import DataResponse
from app.schemas.sche_user import UserItemResponse, UserCreateRequest, UserUpdateMeRequest, UserUpdateRequest, \
    UserTreeResponse
from app.services.srv_user import UserService
from app.models import User
from app.core import error_code, message

logger = logging.getLogger()
router = APIRouter()


@router.get("", dependencies=[Depends(login_required)], response_model=Page[UserItemResponse])
def get(params: PaginationParams = Depends()) -> Any:
    """
    API Get list User
    """
    try:
        _query = db.session.query(User)
        users = paginate(model=User, query=_query, params=params)
        return users
    except Exception as e:
        return HTTPException(status_code=400, detail=logger.error(e))


@router.post("", dependencies=[Depends(PermissionRequired('admin'))], response_model=DataResponse[UserItemResponse])
def create(user_data: UserCreateRequest) -> Any:
    """
    API Create User
    """
    try:
        exist_user = db.session.query(User).filter(User.email == user_data.email).first()
        if exist_user:
            raise CustomException(http_code=400, code=error_code.ERROR_122_EMAIL_ALREADY_EXISTS, message=message.MESSAGE_122_EMAIL_ALREADY_EXISTS )
        new_user = UserService().create_user(user_data)
        return DataResponse().success_response(data=new_user)
    except Exception as e:
        raise CustomException(http_code=400, code='400', message=str(e))


@router.get("/me", dependencies=[Depends(login_required)], response_model=DataResponse[UserItemResponse])
def detail_me(current_user: User = Depends(UserService().get_current_user)) -> Any:
    """
    API get detail current User
    """
    return DataResponse().success_response(data=current_user)


@router.put("/me", dependencies=[Depends(login_required)], response_model=DataResponse[UserItemResponse])
def update_me(user_data: UserUpdateMeRequest,
              current_user: User = Depends(UserService().get_current_user)) -> Any:
    """
    API Update current User
    """
    try:
        if user_data.email is not None:
            exist_user = db.session.query(User).filter(
                User.email == user_data.email, User.id != current_user.id).first()
            if exist_user:
                raise CustomException(http_code=400, code=error_code.ERROR_122_EMAIL_ALREADY_EXISTS, message=message.MESSAGE_122_EMAIL_ALREADY_EXISTS )
        updated_user = UserService().update_me(data=user_data, current_user=current_user)
        return DataResponse().success_response(data=updated_user)
    except Exception as e:
        raise CustomException(http_code=400, code='400', message=str(e))


@router.get("/tree")
def get_tree():
    users = db.session.query(User).order_by(asc(User.id)).all()
    return format_staff_tree(users, None)


@router.get("/{user_id}", dependencies=[Depends(login_required)], response_model=DataResponse[UserItemResponse])
def detail(user_id: int) -> Any:
    """
    API get Detail User
    """
    try:
        exist_user = db.session.query(User).get(user_id)
        if exist_user is None:
            raise CustomException(http_code=400, code=error_code.ERROR_122_EMAIL_ALREADY_EXISTS, message=message.MESSAGE_122_EMAIL_ALREADY_EXISTS )
        return DataResponse().success_response(data=exist_user)
    except Exception as e:
        raise CustomException(http_code=400, code='400', message=str(e))


@router.put("/{user_id}", dependencies=[Depends(PermissionRequired('admin'))],
            response_model=DataResponse[UserItemResponse])
def update(user_id: int, user_data: UserUpdateRequest) -> Any:
    """
    API update User
    """
    try:
        exist_user = db.session.query(User).get(user_id)
        if exist_user is None:
            raise CustomException(http_code=400, code=error_code.ERROR_122_EMAIL_ALREADY_EXISTS, message=message.MESSAGE_122_EMAIL_ALREADY_EXISTS )
        updated_user = UserService().update(user=exist_user, data=user_data)
        return DataResponse().success_response(data=updated_user)
    except Exception as e:
        raise CustomException(http_code=400, code='400', message=str(e))





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
