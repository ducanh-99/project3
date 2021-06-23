import logging

from app.helpers.exception_handler import CustomException
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query
from app.schemas.sche_base import DataResponse, ResponseSchemaBase
from app.services import StaffService
from app.helpers.validate import validate_email
from app.schemas.sche_staff import StaffListRequest, StaffCreateUpdateRequest, StaffUploadFileRequest, \
    StaffUploadFileResponse
from app.helpers.enums import SearchTreeParam
from app.core import error_code, message

logger = logging.getLogger()
router = APIRouter()


@router.post('', response_model=DataResponse)
def create_or_update_staff(staff: StaffCreateUpdateRequest):
    """
        Api POST Create/Update Staff  \n
        APi cho phép tạo mới hoặc update nhân viên tùy theo param truyền vào (nếu có id thì sẽ update, nếu không có id thì sẽ là tạo mới
    Args:\n
        StaffCreateUpdateRequest: schemal tạo mới hoặc thay đổi Team  \n
            id: int (tùy chọn)
            full_name: str
            staff_code: str
            email: email_str
            phone_number: str (10-12 số)
            companies: int
            is_active: bool
    Returns:\n
        id: id của nhân viên 
    Errors:\n
        001: Trường không được để trống (Chưa làm)\n
        004: Trường không hợp lệ (Chưa làm)\n
        061: ID company không tồn tại trong hệ thống\n
        122: Email đã được đăng ký trong hệ thống \n
        124: email nhân viên không đúng định dạng\n
        126: email công ty và email đăng ký không phù hợp\n
        128: Số chứng minh thư không hợp lệ( 9 số hoặc 12 số)\n
        129: Manager không thuộc công ty của nhân viên\n
        130: Manager ID không tồn tại trên hệ thống\n
        131: Định dạng ngày sinh phải là %d/%m/%Y (Chưa làm)\n
        132: phone number phải bắt đầu bằng 0, độ dài tối đa 12 chữ số, tối thiểu 10 chữ số \n
        133: Loại hợp đồng không hợp lệ (Chưa làm) \n
        135: Mã nhân viên trùng nhau\n
    """
    response = {
        'id': 0
    }
    if not staff.id and staff.id != 0:
        response['id'] = StaffService().create(staff_create_request=staff)
    else:
        StaffService().update(staff_update_request=staff)
        response['id'] = staff.id
    return DataResponse().success_response(data=response)


@router.get('/{staff_id}', response_description='Thành công')
def get_detail_staff(staff_id: str):
    """
        Api GET Detail Staff  \n
        APi cho phép lấy chi tiết của nhân viên bao gồm: thông tin cơ bản, phòng ban, nhóm, ...
    Args:\n
        staff_id: int: id của nhân viên cần lấy thông tin
    Returns:\n
        Thông tin chi tiết của nhân viên
    Errors:\n
        001: Trường không được để trống (Chưa làm)\n
        004: Trường không hợp lệ (Chưa làm)\n
        091: ID của staff không tồn tại trong hệ thống \n
        999: Hệ thống đang bảo trì, quý khách vui lòng thử lại sau \n
    """
    if staff_id.isnumeric():
        staff = StaffService().get_detail_with_tree(id=int(staff_id))
    elif validate_email(staff_id):
        staff = StaffService().get_detail_with_email(email=staff_id)
    else:
        raise CustomException(http_code=400, code=error_code.ERROR_004_FIELD_VALUE_INVALID,
                              message=message.MESSAGE_004_FIELD_VALUE_INVALID)
    return DataResponse().success_response(data=staff)


@router.get('', response_model=Any)
def get_list_staffs(department_id: Optional[List[int]] = Query(default=[], alias="department_id[]"),
                    team_id: Optional[List[int]] = Query(default=[], alias="team_id[]"),
                    manager_id: Optional[List[int]] = Query(default=[], alias="manager_id[]"),
                    staff_list_req: StaffListRequest = Depends()):
    """
        API Get list Staff - có phân trang
        API cho phép tìm kiếm thông tin danh sách Staff dựa vào các thuộc tính của Staff\n
        Thuộc tính\n
        - staff_code (Mã Nhân viên)\n
        - Full_name (Tên nhân viên)\n
        Các toán tử được sử dụng: 'LIKE', 'LIKE_BEGIN', 'EQ', 'GE', 'LE', 'GT', 'LT', 'LIST', 'SEQ'\n
        Error Code\n
        - 000:  Thành công\n
        - 002:	Số lượng phần tử trong trang tìm kiếm phải lớn hơn 0\n
        - 003:	Số thứ tự của trang hiện tại phải lớn hơn hoặc bằng 0\n
        - 006:	Các trường tìm kiếm không hợp lệ\n
        - 007:	Các toán tử tìm kiếm không hợp lệ\n
        - 008:	Các toán tử tìm kiếm không phù hợp với trường hoặc giá trị tìm kiếm\n
        - 009:	Số lượng các trường, toán tử và giá trị không hợp lệ\n
        - 092:	ID của company không được để trống\n
        - 051:	Search param: Type phải là tree hoặc list\n
        - 999:	Hệ thống đang bảo trì, quý khách vui lòng thử lại sau\n
    """
    external_param = {
        "department_id": department_id,
        "team_id": team_id,
        "manager_id": manager_id
    }
    if staff_list_req.type.value == SearchTreeParam.TREE.value:
        tree_staffs = StaffService().get_tree(
            company_id=staff_list_req.company_id)
        return DataResponse().success_response(data=tree_staffs)
    else:
        staffs = StaffService().get_list_with_paging(
            staff_list_req=staff_list_req, external_param=external_param)
        return staffs


@router.post('/upload', response_model=DataResponse[StaffUploadFileResponse], response_description='Thành công')
def upload_file_staffs(req_data: StaffUploadFileRequest):
    """
        API Upload file excel Staff
        API cho phép Người dùng nhập dữ liệu theo file excel template và upload lên hệ thống\n
        Cho phép upload tối đa 5000 dòng dữ liệu trong 1 lần import\n
        Download Template tại file_path: Danh-sach-nhan-vien.xlsx\n
        Thuộc tính\n
        - company_id (ID công ty)\n
        - file_path (file_path trả về trong API Upload file)\n
        Error Code\n
        - 000:  Thành công\n
        - 001:	Các trường thông tin không được bỏ trống\n
        - 045:	File không tồn tại hoặc không đúng định dạng\n
        - 061:	ID company không tồn tại trong hệ thống\n
        - 139:	File không đúng template\n
        - 140:	Lỗi dữ liệu, vui lòng check trong file kết quả lỗi\n
        - 999:	Hệ thống đang bảo trì, quý khách vui lòng thử lại sau\n
    """

    total_rows, file_path = StaffService().upload_excel(req_data=req_data)

    if file_path:
        return DataResponse().custom_response(
            code='140',
            message='Lỗi dữ liệu, vui lòng check trong file kết quả lỗi',
            data={
                'total_rows': total_rows,
                'file_path': file_path
            }
        )
    return ResponseSchemaBase().success_response()
