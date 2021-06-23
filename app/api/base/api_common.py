import io
import logging
from io import BytesIO
from typing import Any

from fastapi import File, APIRouter, UploadFile, Path
from starlette.responses import StreamingResponse

from app.helpers.exception_handler import CustomException

from app.helpers.minio_handler import MinioHandler
from app.schemas.sche_base import DataResponse
from app.schemas.sche_common import UploadFileResponse
from app.core import error_code, message

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload/minio", response_model=DataResponse[UploadFileResponse])
async def upload_file_to_minio(file: UploadFile = File(...)):
    try:
        data = file.file.read()
        if len(data) > 1024 * 1024 * 10:
            raise CustomException(http_code=400, code=error_code.ERROR_100_FILE_TOO_LARGE,
                                  message=message.MESSAGE_100_FILE_TOO_LARGE)

        file_name = " ".join(file.filename.strip().split())
        file_ext = file_name.split('.')[-1]
        if file_ext.lower() not in ('jpg', 'png', 'pdf', 'xlsx', 'xls', 'svg', 'pdf', 'doc', 'docx', 'rar', 'zip'):
            raise CustomException(http_code=400, code=error_code.ERROR_045_FORMAT_FILE,
                                  message=message.MESSAGE_045_FORMAT_FILE)

        data_file = MinioHandler().get_instance().put_object(
            file_name=file_name,
            file_data=BytesIO(data),
            content_type=file.content_type
        )
        return DataResponse().success_response(data_file)
    except CustomException as e:
        raise e
    except Exception as e:
        logger.error(str(e))
        if e.__class__.__name__ == 'MaxRetryError':
            raise CustomException(http_code=400, code=error_code.ERROR_101_NOT_CONNECT_MinIO,
                                  message=message.MESSAGE_101_NOT_CONNECT_MinIO)
        raise CustomException(code=error_code.ERROR_999_SERVER, message=message.MESSAGE_999_SERVER)


@router.get("/download/minio/{file_path}")
def download_file_from_minio(
        *, file_path: str = Path(..., title="The relative path to the file", min_length=1, max_length=500)
) -> Any:
    try:
        minio_client = MinioHandler().get_instance()
        if not minio_client.check_file_name_exists(minio_client.bucket_name, file_path):
            raise CustomException(http_code=400, code=error_code.ERROR_045_FORMAT_FILE,
                                  message=message.MESSAGE_045_FORMAT_FILE)

        file = minio_client.client.get_object(minio_client.bucket_name, file_path).read()
        return StreamingResponse(io.BytesIO(file))
    except CustomException as e:
        raise e
    except Exception as e:
        logger.error(str(e))
        if e.__class__.__name__ == 'MaxRetryError':
            raise CustomException(http_code=400, code=error_code.ERROR_101_NOT_CONNECT_MinIO,
                                  message=message.MESSAGE_101_NOT_CONNECT_MinIO)
        raise CustomException(code=error_code.ERROR_999_SERVER, message=message.MESSAGE_999_SERVER)
