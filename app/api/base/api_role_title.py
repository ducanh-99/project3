import logging
from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException

from app.helpers.login_manager import get_current_company
from app.models import Company
from app.schemas.sche_base import DataResponse
from app.schemas.sche_role_title import RoleTitleItemResponse, RoleTitleCreateRequest, RoleTitleListRequest, \
    RoleTitleDetailResponse
from app.services.srv_role_title import RoleTitleService

logger = logging.getLogger()
router = APIRouter()


@router.get('', response_model=DataResponse[List[RoleTitleItemResponse]], response_description='Thành công')
def get(role_title_list_request: RoleTitleListRequest = Depends()) -> Any:
    """
        API Get list Role Title - KHÔNG PHÂN TRANG
        API cho phép tìm kiếm thông tin danh sách Role Title dựa vào các thuộc tính\n
        Thuộc tính\n
        - role_title_name (Tên role_title)\n
        - department_id (id phòng ban)\n
        Error Code\n
        - 000:  Thành công\n
        - 092:	ID của company không được để trống\n
        - 999:	Hệ thống đang bảo trì, quý khách vui lòng thử lại sau\n
    """
    try:
        role_titles = RoleTitleService().get_list(role_title_list_request=role_title_list_request)
        return DataResponse().success_response(data=role_titles)
    except Exception as e:
        raise HTTPException(status_code=400, detail=logger.error(e))


@router.post('', response_description='Thành công')
def create(req_data: RoleTitleCreateRequest) -> Any:
    """
        API create/update Role Title\n
        Cho phép tạo mới hoặc update một job-title.\n
        Một job-title khi tạo mới bắt buộc phải thuộc một company\n
        Important:\n
        - Khi tạo mới job_title trong phòng ban, nếu trùng name với 1 job_title đã có sẵn thì active job_title đó lên & báo thành công\n
        - Không thể khóa một Job title khi job_title đang gắn với một phòng ban đang kích hoạt\n
        - Không thể cập nhật department_id của job title đã tồn tại\n
        - Không thể cập nhật company_id của job title đã tồn tại\n
        Error Code\n
        - 000:  Thành công\n
        - 001:  Các trường thông tin không được bỏ trống\n
        - 061:  ID company không tồn tại trong hệ thống\n
        - 091:  ID của phòng ban không tồn tại trong hệ thống\n
        - 192:  Phòng ban không thuộc trong công ty\n
        - 193:  Không thể khóa vì job title đang gắn với phòng ban đang hoạt động\n
        - 194:  Không thể cập nhật phòng ban của job title đã tồn tại\n
        - 195:  Không thể cập nhật công ty của job title đã tồn tại\n
        - 999:	Hệ thống đang bảo trì, quý khách vui lòng thử lại sau\n
    """
    role_title = RoleTitleService().create_or_update(req_data=req_data)
    return DataResponse().success_response(data={'id': role_title.id})


@router.get('/{role_title_id}', response_model=DataResponse[RoleTitleDetailResponse], response_description='Thành công')
def detail(role_title_id: int) -> Any:
    """
        API get detail Role Title
        API cho phép lấy chi tiết Role Title theo role_title_id\n
        Error Code\n
        - 000:  Thành công\n
        - 191:	role title id không tồn tại\n
        - 999:	Hệ thống đang bảo trì, quý khách vui lòng thử lại sau\n
    """
    role_title = RoleTitleService().detail(role_title_id=role_title_id)
    return DataResponse().success_response(data=role_title)
