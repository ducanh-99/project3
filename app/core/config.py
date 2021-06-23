import os
from dotenv import load_dotenv
from pydantic import BaseSettings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
load_dotenv(os.path.join(BASE_DIR, '.env'))


class Settings(BaseSettings):
    PROJECT_NAME = os.getenv('PROJECT_NAME', '')
    DEBUG = os.getenv('DEBUG', True)
    SECRET_KEY = os.getenv('SECRET_KEY', '')
    BASE_API_PREFIX = os.getenv('BASE_API_PREFIX', '')
    TEKO_API_PREFIX = '/teko'
    DIGI_API_PREFIX = '/digi'
    BACKEND_CORS_ORIGINS = ['*']
    DATABASE_URL = os.getenv('SQL_DATABASE_URL', '')
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7  # Token expired after 7 days
    SECURITY_ALGORITHM = 'HS256'
    LOGGING_CONFIG_FILE = os.path.join(BASE_DIR, 'logging.ini')

    TEKO_SERVICE_TOKEN = os.getenv('TEKO_SERVICE_TOKEN', '')
    DIGI_SERVICE_TOKEN = os.getenv('DIGI_SERVICE_TOKEN', '')

    MINIO_URL = os.getenv('MINIO_URL', '')
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', '')
    MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', '')
    MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', '')


settings = Settings()
