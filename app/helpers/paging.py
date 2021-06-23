import logging
from pydantic import BaseModel, root_validator
from abc import ABC, abstractmethod
from typing import Optional, Generic, Sequence, Type, TypeVar

from sqlalchemy import asc, desc
from sqlalchemy.orm import Query
from pydantic.generics import GenericModel
from contextvars import ContextVar
from app.helpers.exception_handler import CustomException, ValidateException
from app.schemas.sche_base import ResponseSchemaBase, MetadataSchema
from app.core import error_code, message

T = TypeVar("T")
C = TypeVar("C")

logger = logging.getLogger()


class PaginationParams(BaseModel):
    page_size: Optional[int] = 10
    page: Optional[int] = 1
    sort_by: Optional[str] = 'id'
    order: Optional[str] = 'desc'

    @root_validator()
    def validate_data(cls, data):
        page = data.get("page")
        page_size = data.get("page_size")
        order = data.get("order")

        if page <= 0:
            raise ValidateException(
                error_code.ERROR_003_PAGE_LARGE_THAN_0, message.MESSAGE_003_PAGE_LARGE_THAN_0)
        if page_size <= 0 or page_size > 1000:
            raise ValidateException(
                error_code.ERROR_002_PAGE_SIZE_LARGE_THAN_0, message.MESSAGE_002_PAGE_SIZE_LARGE_THAN_0)

        if order not in ['asc', 'desc']:
            raise ValidateException(
                error_code.ERROR_005_ORDER_VALUE_INVALID, message.MESSAGE_005_ORDER_VALUE_INVALID)

        return data


class BasePage(ResponseSchemaBase, GenericModel, Generic[T], ABC):
    data: Sequence[T]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    @abstractmethod
    def create(cls: Type[C], code: str, message: str, data: Sequence[T], metadata: MetadataSchema) -> C:
        pass  # pragma: no cover


class Page(BasePage[T], Generic[T]):
    metadata: MetadataSchema

    @classmethod
    def create(cls, code: str, message: str, data: Sequence[T], metadata: MetadataSchema) -> "Page[T]":
        return cls(
            code=code,
            message=message,
            data=data,
            metadata=metadata
        )


PageType: ContextVar[Type[BasePage]] = ContextVar("PageType", default=Page)


def paginate(model, query: Query, params: Optional[PaginationParams]) -> Page:
    code = '000'
    message = 'Thành công'

    try:
        total = query.count()

        if params.order:
            direction = desc if params.order == 'desc' else asc
            data = query.order_by(direction(getattr(model, params.sort_by))) \
                .limit(params.page_size) \
                .offset(params.page_size * (params.page - 1)) \
                .all()
        else:
            data = query.limit(params.page_size).offset(params.page_size * params.page).all()

        metadata = MetadataSchema(
            current_page=params.page,
            page_size=params.page_size,
            total_items=total
        )

    except Exception as e:
        raise CustomException(code=error_code.ERROR_999_SERVER, message='Bảo trì')
    return PageType.get().create(code, message, data, metadata)
