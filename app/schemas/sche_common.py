import typing
from pathlib import Path
from typing import Type, Any, Union

from fastapi import UploadFile as UploadFileSource
from pydantic import BaseModel, validator
from starlette.datastructures import UploadFile as StarletteUploadFile

from app.helpers.exception_handler import CustomException, ValidateException

from app.core import error_code, message


class UploadFileRequest(UploadFileSource):
    file: typing.IO
    filename: str
    file_data = Union[bytes, str]

    @classmethod
    def validate(cls: Type["UploadFileRequest"], v: Any) -> Any:
        if not isinstance(v, StarletteUploadFile) or not v.file or not v.filename:
            raise CustomException(http_code=400, code=error_code.ERROR_042_FILE_NOT_NULL, message=message.MESSAGE_042_FILE_NOT_NULL)

        path = Path(v.filename)
        if not path.name or path.suffix.lower() not in ['.pdf', '.png', '.jpg', '.rar']:
            raise CustomException(http_code=400, code=error_code.ERROR_045_FORMAT_FILE, message=message.MESSAGE_045_FORMAT_FILE)

        file_data = v.file.read()
        if len(file_data) > 10 * 1024 * 1024:
            raise CustomException(http_code=400, code=error_code.ERROR_100_FILE_TOO_LARGE, message=message.MESSAGE_100_FILE_TOO_LARGE)
        v.file_data = file_data
        return v


class UploadFileResponse(BaseModel):
    bucket_name: str
    file_name: str
    url: str


class DownloadFileRequest(BaseModel):
    relative_path: str

    @validator("relative_path")
    def validate_relative_path(cls, v):
        if len(v) < 1 or len(v) > 500:
            raise ValidateException("004", f"Trường dữ liệu không hợp lệ: Độ dài relative_path phải từ 1-500")
        return v
