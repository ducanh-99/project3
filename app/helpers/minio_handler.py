import logging
import random
from datetime import datetime, timedelta

from minio import Minio
from slugify import slugify

from app.core.config import settings
from app.helpers.exception_handler import CustomException
from app.core import error_code, message

logger = logging.getLogger()


class MinioHandler():
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if not MinioHandler.__instance:
            MinioHandler.__instance = MinioHandler()
        return MinioHandler.__instance

    def __init__(self):
        self.minio_url = settings.MINIO_URL
        self.access_key = settings.MINIO_ACCESS_KEY
        self.secret_key = settings.MINIO_SECRET_KEY
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.client = Minio(
            self.minio_url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )
        self.make_bucket()

    def make_bucket(self) -> str:
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
        return self.bucket_name

    def presigned_get_object(self, bucket_name, object_name):
        # Request URL expired after 7 days
        url = self.client.presigned_get_object(
            bucket_name=bucket_name,
            object_name=object_name,
            expires=timedelta(days=7)
        )
        return url

    def check_file_name_exists(self, bucket_name, file_name):
        try:
            self.client.stat_object(bucket_name=bucket_name, object_name=file_name)
            return True
        except Exception as e:
            logger.debug(e)
            return False

    def put_object(self, file_data, file_name, content_type):
        try:

            file_name = self.normalize_file_name(file_name)
            datetime_prefix = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            object_name = f"{datetime_prefix}___{file_name}"
            while self.check_file_name_exists(bucket_name=self.bucket_name, file_name=object_name):
                random_prefix = random.randint(1, 1000)
                object_name = f"{datetime_prefix}___{random_prefix}___{file_name}"

            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                content_type=content_type,
                length=-1,
                part_size=10 * 1024 * 1024
            )
            url = self.presigned_get_object(bucket_name=self.bucket_name, object_name=object_name)
            data_file = {
                'bucket_name': self.bucket_name,
                'file_name': object_name,
                'url': url
            }
            return data_file
        except Exception as e:
            raise Exception(e)

    def normalize_file_name(self, file_name):
        try:
            file_name = " ".join(file_name.strip().split())
            file_ext = file_name.split('.')[-1]
            file_name = ".".join(file_name.split('.')[:-1])
            file_name = slugify(file_name)
            file_name = file_name[:100]
            file_name = file_name + '.' + file_ext
            return file_name
        except Exception as e:
            logger.error(str(e))
            raise CustomException(http_code=400, code=error_code.ERROR_046_STANDARDIZED, message=message.MESSAGE_046_STANDARDIZED)


def from_file_type_to_mime_type(file_type: str) -> str:
    FILE_TYPE_TO_MIME = {
        'rar': 'application/vnd.rar',
        'zip': 'application/zip',
        'png': 'image/png',
        'pdf': 'application/pdf',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }

    return FILE_TYPE_TO_MIME.get(file_type, 'application/octet-stream')
