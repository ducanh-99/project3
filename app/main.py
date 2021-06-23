import logging

import uvicorn
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.api import router
from app.models import Base
from app.db.base import engine
from app.core.config import settings
from app.helpers.exception_handler import CustomException, http_exception_handler, fastapi_error_handler

logging.config.fileConfig(settings.LOGGING_CONFIG_FILE, disable_existing_loggers=False)
Base.metadata.create_all(bind=engine)


def get_application(testing: bool = False) -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME, openapi_url=f'{settings.BASE_API_PREFIX}/openapi.json',
        docs_url = f'{settings.BASE_API_PREFIX}/docs', redoc_url = None,
        description='HR service to manager staff in VNlife environment',
        debug=settings.DEBUG
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    if testing is False:
        application.add_middleware(DBSessionMiddleware, db_url=settings.DATABASE_URL)
    application.include_router(router=router, prefix=settings.BASE_API_PREFIX)
    application.add_exception_handler(CustomException, http_exception_handler)
    application.add_exception_handler(Exception, fastapi_error_handler)

    return application


app = get_application()
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
