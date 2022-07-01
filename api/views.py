from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.


def test(request):
    import json

    if request.method == "POST":
        print("POST")
        print(request.body)
        print("!@###############")
        print(request.POST)
        return JsonResponse(
            {
                "success": True,
                "message": "Test successful",
                "error": None,
            }
        )
    return JsonResponse(
        {"success": False, "message": "Test POST method required", "error": "400"},
        status=400,
    )


def docs(request):
    return JsonResponse(
        {
            "đăng ký": {
                "method": "POST",
                "url": "http://dhqit.ddns.net/api/register",
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
                "url": "http://dhqit.ddns.net/api/login",
                "payload": {
                    "username": "username hoặc phone hoặc email hoặc id",
                    "password": "bắt buộc",
                },
            },
            "lấy thông tin user": {
                "method": "GET",
                "url": "http://dhqit.ddns.net/api/get_profile",
                "token": "Bearer <token>",
            },
            "sửa thông tin user": {
                "method": "POST",
                "url": "http://dhqit.ddns.net/api/edit_profile",
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
                "url": "http://dhqit.ddns.net/api/set_avatar",
                "token": "Bearer <token>",
                "formdata": {"avatar": "1 file ảnh đuôi jpeg/jpg/png"},
            },
            "cuộc hội thoại gần đây": {
                "method": "GET",
                "url": "http://dhqit.ddns.net/api/get_recent_messages",
                "token": "Bearer <token>",
            },
            "gửi tin nhắn": {
                "method": "POST",
                "url": "http://dhqit.ddns.net/api/add_new_message",
                "token": "Bearer <token>",
                "formdata": {
                    "room_id": "id của cuộc hội thoại hoặc id của người dùng",
                    "type": [
                        "text",
                        "image",
                        "video",
                        "audio",
                        "file",
                    ],
                    "reply_to": "id của tin nhắn để trả lời(nếu có)",
                    "text": "nội dung tin nhắn nếu type = text",
                    "image": "1 file ảnh đuôi jpeg/jpg/png nếu type = image",
                    "video": "1 file video đuôi mp4/mov nếu type = video",
                    "audio": "1 file audio đuôi mp3/wav nếu type = audio",
                    "file": "1 file nếu type = file",
                },
            },
            "tạo group": {
                "method": "POST",
                "url": "http://dhqit.ddns.net/api/create_group",
                "token": "Bearer <token>",
                "formdata": {
                    "name": "tên group",
                    "members_can_change_info": "0 hoặc 1",
                    "avatar": "1 file ảnh đuôi jpeg/jpg/png(nếu có)",
                },
            },
            "thêm người dùng vào group": {
                "method": "POST",
                "url": "http://dhqit.ddns.net/api/add_user_to_group",
                "token": "Bearer <token>",
                "payload": {
                    "group_id": "id của group",
                    "user_id": "id của người dùng",
                },
            },
            "chỉnh sửa group": {
                "method": "POST",
                "url": "http://dhqit.ddns.net/api/group_settings",
                "token": "Bearer <token>",
                "formdata": {
                    "members_can_change_info": "0 hoặc 1(nếu có)",
                    "avatar": "1 file ảnh đuôi jpeg/jpg/png(nếu có)",
                    "name": "tên group(nếu có)",
                },
            },
            "xóa người dùng khỏi group": {
                "method": "POST",
                "url": "http://dhqit.ddns.net/api/remove_user_from_group",
                "token": "Bearer <token>",
                "payload": {
                    "group_id": "id của group",
                    "user_id": "id của người dùng",
                },
            },
            "xóa group": {
                "method": "POST",
                "url": "http://dhqit.ddns.net/api/delete_group",
                "token": "Bearer <token>",
                "payload": {"group_id": "id của group"},
            },
            "tìm kiếm người dùng": {
                "method": "GET",
                "url": "http://dhqit.ddns.net/api/search_user",
                "param": "q",
            },
            "thả biểu tượng cảm xúc vào tin nhắn": {
                "method": "POST",
                "url": "http://dhqit.ddns.net/api/react_to_message",
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
        }
    )
