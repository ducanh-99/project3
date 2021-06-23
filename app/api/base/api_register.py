from typing import Any

from fastapi import APIRouter, Depends
from fastapi_sqlalchemy import db

from app.helpers.exception_handler import CustomException
from app.models import User
from app.schemas.sche_base import DataResponse
from app.schemas.sche_user import UserItemResponse, UserRegisterRequest
from app.services.srv_user import UserService
from app.core import error_code, message

router = APIRouter()


@router.post('', response_model=DataResponse[UserItemResponse])
def register(register_data: UserRegisterRequest) -> Any:
    try:
        exist_user = db.session.query(User).filter(User.email == register_data.email).first()
        if exist_user:
            raise CustomException(http_code=400, code=error_code.ERROR_122_EMAIL_ALREADY_EXISTS, message=message.MESSAGE_122_EMAIL_ALREADY_EXISTS)
        register_user = UserService().register_user(register_data)
        return DataResponse().success_response(data=register_user)
    except Exception as e:
        raise CustomException(http_code=400, code='400', message=str(e))
