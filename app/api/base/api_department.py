import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.helpers.enums import SearchTreeParam
from app.schemas.sche_base import DataResponse, ResponseSchemaBase
from app.schemas.sche_department import DepartmentListRequest, DepartmentCreateRequest, DepartmentDetailResponse, \
    DepartmentAddStaffRequest, DepartmentUpdateStaffRequest
from app.services.srv_department import DepartmentService

logger = logging.getLogger()
router = APIRouter()


@router.get('', response_model=Any, response_description='Thành công')
def get(department_list_req: DepartmentListRequest = Depends()) -> Any:
    """
        API Get list Department - có phân trang
        API cho phép tìm kiếm thông tin danh sách Department\n
        Thuộc tính tìm kiếm\n
        - department_name (Tên phòng ban)\n
        - parent_id (ID phòng ban cấp trên)\n
        Error Code\n
        - 000:  Thành công\n
        - 002:	Số lượng phần tử trong trang tìm kiếm phải lớn hơn 0\n
        - 003:	Số thứ tự của trang hiện tại phải lớn hơn hoặc bằng 0\n
        - 092:	ID của company không được để trống\n
        - 051:	Search param: Type phải là tree hoặc list\n
        - 999:	Hệ thống đang bảo trì, quý khách vui lòng thử lại sau\n
    """
    try:
        if department_list_req.type.value == SearchTreeParam.TREE.value:
            tree_departments = DepartmentService().get_tree(company_id=department_list_req.company_id)
            return DataResponse().success_response(data=tree_departments)
        else:
            departments = DepartmentService().get_list_with_paging(department_list_req=department_list_req)
            return departments
    except Exception as e:
        raise HTTPException(status_code=400, detail=logger.error(e))


@router.get('/{department_id}', response_model=DataResponse[DepartmentDetailResponse],
            response_description='Thành công')
def detail(department_id: int) -> Any:
    """
        API get detail Department\n
        Trả về chi tiết department, sơ đồ cây các department cấp dưới và danh sách staff trong department\n
        Tham số đầu vào: department_id\n
        Error Code\n
        - 000:  Thành công\n
        - 091:	ID của phòng ban không tồn tại trong hệ thống \n
        - 999:	Hệ thống đang bảo trì, quý khách vui lòng thử lại sau\n
    """
    department = DepartmentService().get_detail(id=department_id)
    return DataResponse().success_response(data=department)


@router.post('', response_description='Thành công')
def create(req_data: DepartmentCreateRequest) -> Any:
    """
        API create Department\n
        Cho phép tạo mới hoặc update một department.\n
        Một department khi tạo mới bắt buộc phải thuộc một company\n
        Important:\n
        Không được phép khóa phòng ban đang có nhân viên\n
        Không được phép khóa phòng ban mà các phòng ban trực thuộc đang có nhân viên \n
        Khi khóa phòng ban thì các phòng ban trực thuộc cũng bị khóa theo \n
        Khi khóa phòng ban thì thông tin về phòng ban đó (level và job-titles ) sẽ bị khóa theo\n
        Error Code\n
        - 000:  Thành công\n
        - 001:  Các trường thông tin không được bỏ trống\n
        - 061:  ID company không tồn tại trong hệ thống\n
        - 091:  ID của phòng ban không tồn tại trong hệ thống\n
        - 092:  ID của company không được để trống \n
        - 093:  Mã phòng ban bị trùng nhau \n
        - 094:  ID của phòng ban cấp trên không tồn tại trong hệ thống \n
        - 095:  Không được phép xóa phòng ban đang có nhân viên \n
        - 096:  Không thể xóa phòng ban do các phòng ban trực thuộc đang có nhân viên \n
        - 990:	Hệ thống đang bảo trì, quý khách vui lòng thử lại sau\n
        - 999:	Hệ thống đang bảo trì, quý khách vui lòng thử lại sau\n
    """
    department = DepartmentService().create_or_update(req_data=req_data)
    return DataResponse().success_response(data={'id': department.id})


@router.post('/staff/add', response_description='Thành công')
def add_staff(req_data: DepartmentAddStaffRequest) -> Any:
    """
        API add Staff to Department\n
        Cho phép thêm một danh sách staff vào department.\n
        Staff và department khi tạo mới bắt buộc phải thuộc cùng một company\n
        Role_title phải thuộc Department\n
        Important:\n
        Nếu Staff đã thuộc department từ trước rồi thì đổi trạng thái is_active = True\n
        Trong một công ty, một Staff chỉ thuộc một department - nếu trong list staff có staff thuộc department khác thì raise báo lỗi\n
        Error Code\n
        - 000:  Thành công\n
        - 091:  ID của phòng ban không tồn tại trong hệ thống\n
        - 097:  Nhân viên và phòng ban không thuộc cùng công ty \n
        - 098:  Role_title không thuộc phòng ban \n
        - 107:  Phòng ban đã bị inactive \n
        - 134:  id của staff không tồn tại \n
        - 990:	Hệ thống đang bảo trì, quý khách vui lòng thử lại sau\n
        - 999:	Hệ thống đang bảo trì, quý khách vui lòng thử lại sau\n
    """
    DepartmentService().add_staff(req_data=req_data)
    return ResponseSchemaBase().success_response()


@router.put('/staff/update', response_description='Thành công')
def update_staff(req_data: DepartmentUpdateStaffRequest) -> Any:
    """
        API create/update Staff in Department\n
        Cho phép chỉnh sửa một staff trong department.\n
        Role_title phải thuộc Department\n
        Important:\n
        Trong 1 công ty. nếu Staff chưa thuộc Department nào thì tạo mới Department-Staff\n
        Trong 1 công ty, nếu Staff đang thuộc 1 Department (Department-Staff đang active) thì chỉ cho phép update Department-Staff đó, còn lại raise lỗi\n
        Trong 1 công ty, nếu Staff không thuộc Department nào (tất cả Department-Staff đang inactive):\n
        - Department trùng với Department-Staff đã có => update\n
        - Department ko trùng với Department-Staff đã có => create\n
        Error Code\n
        - 000:  Thành công\n
        - 091:  ID của phòng ban không tồn tại trong hệ thống\n
        - 097:  Nhân viên và phòng ban không thuộc cùng công ty \n
        - 098:  Role_title không thuộc phòng ban \n
        - 105:  Staff đã thuộc department khác \n
        - 134:  id của staff không tồn tại \n
        - 191:  role id không tồn tại \n
        - 990:	Hệ thống đang bảo trì, quý khách vui lòng thử lại sau\n
        - 999:	Hệ thống đang bảo trì, quý khách vui lòng thử lại sau\n
    """
    DepartmentService().create_or_update_staff(req_data=req_data)
    return ResponseSchemaBase().success_response()
