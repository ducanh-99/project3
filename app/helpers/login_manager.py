from fastapi import HTTPException, Depends
from fastapi_sqlalchemy import db

from app.core.config import settings
from app.models import User, Company
from app.services.srv_user import UserService
from app.helpers.exception_handler import CustomException
from app.core import error_code, message


def login_required(http_authorization_credentials=Depends(UserService().reusable_oauth2)):
    return UserService().get_current_user(http_authorization_credentials)


def get_current_company(http_authorization_credentials=Depends(UserService().reusable_oauth2)) -> Company:
    if http_authorization_credentials.credentials == settings.TEKO_SERVICE_TOKEN:
        company_name = 'Teko'
    elif http_authorization_credentials.credentials == settings.DIGI_SERVICE_TOKEN:
        company_name = 'Digilife'
    else:
        raise CustomException(http_code=400, code=error_code.ERROR_040_UNAUTHORIZED, message=message.MESSAGE_040_UNAUTHORIZED) 
    return db.session.query(Company).filter(Company.company_name == company_name).first()


class PermissionRequired:
    def __init__(self, *args):
        self.user = None
        self.permissions = args

    def __call__(self, user: User = Depends(login_required)):
        self.user = user
        if self.user.role not in self.permissions and self.permissions:
            raise HTTPException(status_code=400,
                                detail=f'User {self.user.email} can not access this api')


class AppTokenRequired:
    def __init__(self, *args):
        self.service_name = args[0]

    def __call__(self, http_authorization_credentials=Depends(UserService().reusable_oauth2)):
        if self.service_name == 'teko':
            if http_authorization_credentials.credentials != settings.TEKO_SERVICE_TOKEN:
                raise CustomException(http_code=400, code=error_code.ERROR_040_UNAUTHORIZED, message=message.MESSAGE_040_UNAUTHORIZED)
        if self.service_name == 'digi':
            if http_authorization_credentials.credentials != settings.DIGI_SERVICE_TOKEN:
                raise CustomException(http_code=400, code=error_code.ERROR_040_UNAUTHORIZED, message=message.MESSAGE_040_UNAUTHORIZED)
