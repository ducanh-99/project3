import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi_sqlalchemy import db

from app.helpers.paging import PaginationParams, paginate, Page
from app.models import Company
from app.schemas.sche_company import CompanyItemResponse

logger = logging.getLogger()
router = APIRouter()


@router.get("", response_model=Page[CompanyItemResponse])
def get(params: PaginationParams = Depends()) -> Any:
    """
    API Get list Company
    """
    try:
        _query = db.session.query(Company)
        companies = paginate(model=Company, query=_query, params=params)
        return companies
    except Exception as e:
        return HTTPException(status_code=400, detail=logger.error(e))
