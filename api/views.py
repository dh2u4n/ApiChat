from django.shortcuts import render
from django.http import JsonResponse

from ApiChat.settings import HOST_URL


def test(request):
    return JsonResponse({"test": "test", "len": len(request.FILES)})


def docs(request):
    return JsonResponse(
        {
            "đăng ký": {
                "method": "POST",
                "url": HOST_URL + "/api/register",
                "payload": {
                    "username": "bắt buộc",
                    "email": "bắt buộc",
                    "phone": "không bắt buộc",
                    "password": "bắt buộc",
                    "first_name": "bắt buộc",
                    "last_name": "bắt buộc",
                },
            },
            "đăng nhập": {
                "method": "POST",
                "url": HOST_URL + "/api/login",
                "payload": {
                    "username": "username hoặc phone hoặc email hoặc id",
                    "password": "bắt buộc",
                },
            },
            "lấy thông tin user": {
                "method": "GET",
                "url": HOST_URL + "/api/get_profile",
                "token": "Bearer <token>",
            },
            "sửa thông tin user": {
                "method": "POST",
                "url": HOST_URL + "/api/edit_profile",
                "token": "Bearer <token>",
                "payload": {
                    "password": "bắt buộc",
                    "username": "thêm nếu đổi",
                    "email": "thêm nếu đổi",
                    "phone": "thêm nếu đổi",
                    "first_name": "thêm nếu đổi",
                    "last_name": "thêm nếu đổi",
                    "new_password": "thêm nếu đổi",
                },
            },
            "cài avatar": {
                "method": "POST",
                "url": HOST_URL + "/api/set_avatar",
                "token": "Bearer <token>",
                "formdata": {"avatar": "1 file ảnh đuôi jpeg/jpg/png"},
            },
            "cuộc hội thoại gần đây": {
                "method": "GET",
                "url": HOST_URL + "/api/get_recent_messages",
                "token": "Bearer <token>",
            },
            "gửi tin nhắn": {
                "method": "POST",
                "url": HOST_URL + "/api/send_message",
                "token": "Bearer <token>",
                "formdata": {
                    "room_id": "id của cuộc hội thoại hoặc id của người dùng",
                    "reply_to": "id của tin nhắn để trả lời(nếu có)",
                    "text": "nếu có",
                    "file{i}": "nếu có(i bắt đầu từ 1)",
                },
            },
            "tạo group": {
                "method": "POST",
                "url": HOST_URL + "/api/create_group",
                "token": "Bearer <token>",
                "formdata": {
                    "name": "tên group",
                    "members_can_change_info": "0 hoặc 1",
                    "avatar": "1 file ảnh đuôi jpeg/jpg/png(nếu có)",
                },
            },
            "thêm người dùng vào group": {
                "method": "POST",
                "url": HOST_URL + "/api/add_user_to_group",
                "token": "Bearer <token>",
                "payload": {
                    "group_id": "id của group",
                    "user_id": "id của người dùng",
                },
            },
            "chỉnh sửa group": {
                "method": "POST",
                "url": HOST_URL + "/api/group_settings",
                "token": "Bearer <token>",
                "formdata": {
                    "members_can_change_info": "0 hoặc 1(nếu có)",
                    "avatar": "1 file ảnh đuôi jpeg/jpg/png(nếu có)",
                    "name": "tên group(nếu có)",
                },
            },
            "xóa người dùng khỏi group": {
                "method": "POST",
                "url": HOST_URL + "/api/remove_user_from_group",
                "token": "Bearer <token>",
                "payload": {
                    "group_id": "id của group",
                    "user_id": "id của người dùng",
                },
            },
            "xóa group": {
                "method": "POST",
                "url": HOST_URL + "/api/delete_group",
                "token": "Bearer <token>",
                "payload": {"group_id": "id của group"},
            },
            "tìm kiếm người dùng": {
                "method": "GET",
                "url": HOST_URL + "/api/search_user",
                "param": "q",
            },
            "thả biểu tượng cảm xúc vào tin nhắn": {
                "method": "POST",
                "url": HOST_URL + "/api/react_to_message",
                "token": "Bearer <token>",
                "payload": {
                    "message_id": "id của tin nhắn",
                    "reaction": [
                        "like",
                        "love",
                        "haha",
                        "wow",
                        "sad",
                        "angry",
                        None,
                    ],
                },
                "lưu ý": "reaction = null thì gỡ biểu tượng cảm xúc đã thả",
            },
            "lấy danh sách tin nhắn của 1 room": {
                "method": "GET",
                "url": HOST_URL + "/api/get_messages",
                "token": "Bearer <token>",
                "param": "room_id, page",
            },
            "danh sách tin nhắn đang chờ": {
                "method": "GET",
                "url": HOST_URL + "/api/get_pending_messages",
                "token": "Bearer <token>",
            },
            "lấy lại mật khẩu": {
                "method": "POST",
                "url": HOST_URL + "/api/reset_pw",
                "payload": {
                    "email": "email của người dùng",
                    "otp_code": "mã xác nhận",
                    "new_password": "mật khẩu mới",
                },
                "ghi chú": "để mỗi email server gửi otp về, sau đấy thêm otp với mật khẩu mới",
            },
        }
    )
