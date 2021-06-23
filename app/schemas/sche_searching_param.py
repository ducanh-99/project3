from typing import Optional

from pydantic import BaseModel, root_validator

from app.helpers.constant import SearchOperator
from app.helpers.exception_handler import ValidateException


class SearchingParamSchema(BaseModel):
    field_values: Optional[str]
    operators: Optional[str]
    values: Optional[str]

    @classmethod
    def create(cls, input_field_values, input_operators, input_values):
        cls.field_values = input_field_values
        cls.operators = input_operators
        cls.values = input_values

    @root_validator()
    def params_valid(cls, params):
        fields = params.get("field_values").split(";") if params.get("field_values") else []
        operators = params.get("operators").split(";") if params.get("operators") else []
        values = params.get("values").split(";") if params.get("values") else []

        if not len(fields) == len(operators) == len(values):
            raise ValidateException("009", "Số lượng các trường, toán tử và giá trị không hợp lệ")

        for operator in operators:
            if operator and operator not in SearchOperator().get_list():
                raise ValidateException("007", "Các toán tử tìm kiếm không hợp lệ")
        return params
