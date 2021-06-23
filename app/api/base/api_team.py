from app.helpers.paging import Page
from app.services.srv_staff import StaffService
from typing import Any, Optional
import logging

from fastapi import APIRouter, Depends
from app.schemas.sche_team import TeamCreateRequest, TeamDetailResponse, TeamItemResponse, TeamListRequest, TeamUpdateRequest
from app.schemas.sche_base import DataResponse
from app.schemas.sche_staff import StaffCreate, StaffList, StaffRequest, StaffsRequest
from app.services.srv_team import TeamService
from app.helpers.login_manager import get_current_company
from app.models.model_company import Company


logger = logging.getLogger()
router = APIRouter()


@router.get('', response_model=Page[TeamItemResponse])
def get_list_team(team_list_req: TeamListRequest = Depends()):
    """
        API Get Team - có phân trang
        API cho phép tìm kiếm thông tin danh sách Team dựa vào các thuộc tính của Team\n
        Thuộc tính\n
        - name (Tên nhóm)\n
        Các toán tử được sử dụng: 'LIKE', 'LIKE_BEGIN', 'EQ', 'GE', 'LE', 'GT', 'LT', 'LIST', 'SEQ'\n
        Error Code\n
        - 000:  Thành công\n
        - 002:	Số lượng phần tử trong trang tìm kiếm phải lớn hơn 0\n
        - 003:	Số thứ tự của trang hiện tại phải lớn hơn hoặc bằng 0\n
        - 006:	Các trường tìm kiếm không hợp lệ\n
        - 007:	Các toán tử tìm kiếm không hợp lệ\n
        - 008:	Các toán tử tìm kiếm không phù hợp với trường hoặc giá trị tìm kiếm\n
        - 009:	Số lượng các trường, toán tử và giá trị không hợp lệ\n
        - 999:	Hệ thống đang bảo trì, quý khách vui lòng thử lại sau\n
    """
    list_team = TeamService().get_list_with_paging(team_list_req=team_list_req)
    return list_team


@router.get('/{team_id}', response_model=DataResponse[TeamDetailResponse], response_model_exclude_unset=True)
def get_detail(team_id: int):
    """
        Api Get Team detail \n
        APi cho phép tìm kiếm một dự liệu chi tiết của Một nhóm trong cơ sở dữ liệu
    Args:\n
        team_id (int): Id của nhóm cần lấy thông \n
    Returns:\n
        TeamDetailResponse:\n    
            id: int\n
            team_name: str\n
            company_id: int\n
            created_at: datetime\n
            updated_at: datetime\n
    Errors:\n
        - 001: Trường không được để trống (Chưa làm)\n
        - 004: Trường không hợp lệ (Chưa làm)\n
        - 161: Team id chưa tồn tại\n
        - 999: Hệ thống đang bảo trì, quý khách vui lòng thử lại sau\n
    """
    detail_team = TeamService().get_detail(id=team_id)
    return DataResponse().success_response(data=detail_team)


@router.post('', response_model=DataResponse[TeamCreateRequest], response_description='Thành công', response_model_exclude_unset=True)
def create(data: TeamCreateRequest) -> Any:
    """
        Api Get Create/Update Team  \n
        APi cho phép tạo mới hoặc update tùy theo param truyền vào (nếu có id thì sẽ update, nếu không có id thì sẽ là tạo mới
    Args:\n
        TeamRequest: schemal tạo mới hoặc thay đổi Team  \n
            id: int (tùy chọn)
            team_name: str
            description: str (tùy chọn)
            is_active: bool 
            company_id: int (tùy chọn, chưa được thay đổi công ty khi tạo mới team)
    Returns:\n
        TeamDetailResponse:\n    
            id: int\n
            team_name: str\n
            company_id: int\n
            created_at: datetime\n
            updated_at: datetime\n
    Errors:\n
        001: Trường không được để trống (Chưa làm)\n
        004: Trường không hợp lệ (Chưa làm)\n
        061: ID company không tồn tại trong hệ thống \n
        160: Team đã tồn tại trong hệ thống ( cùng công ty sẽ thông báo lỗi, khác công ty thì không sao)\n
        161: Team id chưa tồn tại\n
        999: Hệ thống đang bảo trì, quý khách vui lòng thử lại sau\n
    """
    if  data.id == 0 or data.id:
        team = TeamService().update(id=data.id, data=data)
    else:
        team = TeamService().create(data=data)
    return DataResponse().success_response(data=team)


@router.post('/staff/add', response_model=DataResponse, response_model_exclude_unset=True)
def add_staffs(staffs: StaffsRequest):
    """[summary] \n
        Api thêm mới danh sách staff vào một team 
    Args:\n
        staffs (StaffsRequest)

    Returns:\n
        200: Thành công
    Errors:\n
        001: Trường không được để trống (Chưa làm)\n
        004: Trường không hợp lệ (Chưa làm)\n
        134: id của staff không tồn \n
        161: Id của team không tồn tại\n
        162: Nhân viên và nhóm không cùng thuộc một công ty\n
        999: Hệ thống đang bảo trì, quý khách vui lòng thử lại sau\n
    """
    create_staffs = TeamService().add_staffs(data=staffs)
    return DataResponse().success_response(data=None)


@router.put('/staff/update', response_model=DataResponse, response_model_exclude_unset=True)
def update_staff(update_data: StaffRequest):
    """[summary] \n
        Api thêm mới danh sách staff vào một team 
    Args:\n
        staff (StaffRequest):\n
            id: int \n
            staff_id: int \n
            role: str (tuy chon)
            is_active: bool
    Returns:\n
        200: Thành công
    Errors:\n
        001: Trường không được để trống (Chưa làm)\n
        004: Trường không hợp lệ (Chưa làm)\n
        134: id của staff không tồn \n
        161: Id của team không tồn tại\n
        162: Nhân viên và nhóm không cùng thuộc một công ty\n
        999: Hệ thống đang bảo trì, quý khách vui lòng thử lại sau\n
    """
    staff = TeamService().update_staff(data=update_data)
    return DataResponse().success_response(data=None)
