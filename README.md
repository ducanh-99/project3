# HR Service

## Mô tả
Manager Hr orgchart

## Installation
**Cách 1:**
- Clone Project
- Cài đặt Postgresql & Create Database
- Cài đặt requirements.txt
- Run project ở cổng 8000
```
// Tạo postgresql Databases via CLI (Ubuntu 20.04)
$ sudo -u postgres psql
# CREATE DATABASE hr_service;
# CREATE USER db_user WITH PASSWORD 'secret123';
# GRANT ALL PRIVILEGES ON DATABASE hr_service TO db_user;
```

```
// Clone project & run
$ git clone git@git.teko.vn:digi-life/o2o/hr-service.git
$ cd hr-service
$ virtualenv -p python3 .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ cp env.example .env       // Recheck SQL_DATABASE_URL ở bước này
$ alembic upgrade head
$ uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
**Cách 2:** Dùng Docker & Docker Compose - đơn giản hơn nhưng cần có kiến thức Docker
- Clone Project
- Run docker-compose
```
$ git clone git@git.teko.vn:digi-life/o2o/hr-service.git
$ cd hr-service
$ docker-compose up -d      # auto build docker image depend on Dockerfile & run service
$ docker-compose build      # build docker image depend on Dockerfile
```

## Cấu trúc project
```
.  
├── alembic  
│   ├── versions    // thư mục chứa file migrations  
│   └── env.py  
├── app  
│   ├── api         // các file api được đặt trong này  
│   ├── core        // chứa file config load các biến env & function tạo/verify JWT access-token  
│   ├── db          // file cấu hình make DB session  
│   ├── helpers     // các function hỗ trợ như login_manager, paging  
│   ├── models      // Database model, tích hợp với alembic để auto generate migration  
│   ├── schemas     // Pydantic Schema  
│   ├── services    // Chứa logic CRUD giao tiếp với DB  
│   └── main.py     // cấu hình chính của toàn bộ project  
├── tests  
│   ├── api         // chứa các file test cho từng api  
│   ├── faker       // chứa file cấu hình faker để tái sử dụng  
│   ├── .env        // config DB test  
│   └── conftest.py // cấu hình chung của pytest  
├── .gitignore  
├── alembic.ini  
├── docker-compose.yaml  
├── Dockerfile  
├── env.example  
├── logging.ini     // cấu hình logging  
├── postgresql.conf // file cấu hình postgresql, sử dụng khi run docker-compose  
├── pytest.ini      // file setup cho pytest  
├── README.md  
└── requirements.txt
```

## Migration
```
$ alembic revision --autogenerate   # Create migration versions depend on changed in models
$ alembic upgrade head   # Upgrade to last version migration
$ alembic downgrade -1   # Downgrade to before version migration
```
