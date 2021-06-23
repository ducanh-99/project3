from typing import Type, TypeVar

from sqlalchemy import func

from app.helpers.constant import SearchOperator
from app.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseService:
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def filter_with_list_params(self, query, request_params):
        _query = query

        for field, operator, value in list(zip(
                request_params.field_values.split(';') if request_params.field_values else [],
                request_params.operators.split(';') if request_params.operators else [],
                request_params.values.split(';') if request_params.values else []
        )):
            if field and operator and value:
                _query = self.add_filter(query=query, field=field, operator=operator, value=value)

        return _query

    def add_filter(self, query, field, operator, value):
        if value is None:
            return query
        switch = {
            SearchOperator.EQUAL: self.filter_equal,
            SearchOperator.LIKE: self.filter_like,
            SearchOperator.LIKE_BEGIN: self.filter_like_begin,
            SearchOperator.GREATER: self.filter_greater,
            SearchOperator.GREATER_EQUAL: self.filter_greater_or_equal,
            SearchOperator.LESS: self.filter_less_than,
            SearchOperator.LESS_EQUAL: self.filter_less_than_or_equal,
            SearchOperator.IN_LIST: self.filter_in_list,
            SearchOperator.SIMILAR_EQUAL: self.filter_similar_equal,
        }
        filter_func = switch.get(operator)
        if filter_func is not None:
            return filter_func(query, field, value)
        return None

    def filter_equal(self, query, field, value):
        f = getattr(self.model, field)
        return query.filter(f == value)

    def filter_similar_equal(self, query, field, value):
        f = getattr(self.model, field)
        return query.filter(func.replace(func.lower(f), ' ', '') == value.replace(' ', '').lower())

    def filter_like(self, query, field, value):
        f = getattr(self.model, field)
        return query.filter(f.ilike('%' + value + '%'))

    def filter_like_begin(self, query, field, value):
        f = getattr(self.model, field)
        return query.filter(f.ilike(value + '%'))

    def filter_greater(self, query, field, value):
        f = getattr(self.model, field)
        return query.filter(f > value)

    def filter_greater_or_equal(self, query, field, value):
        f = getattr(self.model, field)
        return query.filter(f >= value)

    def filter_less_than(self, query, field, value):
        f = getattr(self.model, field)
        return query.filter(f < value)

    def filter_less_than_or_equal(self, query, field, value):
        f = getattr(self.model, field)
        return query.filter(f <= value)

    def filter_in_list(self, query, field, value):
        f = getattr(self.model, field)
        if type(value) != list:
            value = value.split(",")
        return query.filter(f.in_(value))
