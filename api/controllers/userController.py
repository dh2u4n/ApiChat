from api.models.user import User
from .regex import *

from django.db.models import Q  # for search_user
from django.http import JsonResponse
from ApiChat.settings import SECRET_KEY
from ApiChat.settings import HOST_URL

# SECRET_KEY = "quan"

import jwt  # pip install PyJWT
import hashlib
import json
import datetime


def register(request):
    if request.method == "POST":
        try:
            DATA = json.loads(request.body)
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid JSON, maybe data is not in JSON format",
                    "error": "400",
                },
                status=400,
            )

        try:
            username = regex_username(DATA["username"].strip())
            email = regex_email(DATA["email"].strip())
            phone = regex_phone(DATA["phone"].strip()) if "phone" in DATA else None
            password = regex_password(DATA["password"].strip())
            first_name = regex_name(DATA["first_name"].strip())
            last_name = regex_name(DATA["last_name"].strip())
        except KeyError:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Missing required fields",
                    "error": "400",
                },
                status=400,
            )
        except Exception as e:
            print("#######################")
            print(e)
            print("#######################")
            return JsonResponse(
                {
                    "success": False,
                    "message": e.message,
                    "error": "400",
                },
                status=400,
            )

        if (
            User.objects.filter(username=username).exists()
            or User.objects.filter(email=email).exists()
        ):
            return JsonResponse(
                {
                    "success": False,
                    "message": "User already exists with this username or email",
                    "error": "409",
                },
                status=409,
            )

        user = User.objects.create(
            username=username,
            email=email,
            phone=phone,
            password=hashlib.sha256(password.encode("utf-8")).hexdigest(),
            first_name=first_name,
            last_name=last_name,
        )

        token = jwt.encode(
            {
                "uid": user.id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
                "iat": datetime.datetime.utcnow(),
            },
            SECRET_KEY,
            algorithm="HS256",
        )

        if type(token) == bytes:
            token = token.decode("utf-8")

        return JsonResponse(
            {
                "success": True,
                "message": "User created successfully",
                "user": user.toJSON(),
                "token": token,
            },
            status=201,
        )

    else:  # not a POST request
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request method",
                "error": "400",
            },
            status=400,
        )


def login(request):
    if request.method == "POST":
        try:
            DATA = json.loads(request.body)
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid JSON, maybe data is not in JSON format",
                    "error": "400",
                },
                status=400,
            )

        try:
            username = DATA["username"]
            password = DATA["password"]
        except KeyError:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Missing required fields",
                    "error": "400",
                },
                status=400,
            )
        if not username or not password:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Data isn't valid",
                    "error": "400",
                },
                status=400,
            )
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(phone=username)
                except User.DoesNotExist:
                    try:
                        user = User.objects.get(id=username)
                    except User.DoesNotExist:
                        return JsonResponse(
                            {
                                "success": False,
                                "message": "User does not exist",
                                "error": "404",
                            },
                            status=404,
                        )

        if not user.checkPassword(password):
            return JsonResponse(
                {"success": False, "message": "Invalid password", "error": "401"},
                status=401,
            )

        if not user.is_active:
            return JsonResponse(
                {
                    "success": False,
                    "message": "User has been banned",
                    "error": "401",
                },
                status=401,
            )

        token = jwt.encode(
            {
                "uid": user.id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
                "iat": datetime.datetime.utcnow(),
            },
            SECRET_KEY,
            algorithm="HS256",
        )

        if type(token) == bytes:
            token = token.decode("utf-8")

        return JsonResponse(
            {
                "success": True,
                "message": "User logged in successfully",
                "user": user.toJSON(),
                "token": token,
            },
            status=200,
        )

    else:  # not a POST request
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request method",
                "error": "400",
            },
            status=400,
        )


def get_profile(request):
    if request.method == "GET":
        try:
            token = request.headers["Authorization"].split(" ")[1]
        except KeyError:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Missing required fields",
                    "error": "400",
                },
                status=400,
            )
        try:
            uid = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])["uid"]

        except jwt.ExpiredSignatureError:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Token expired",
                    "error": "401",
                },
                status=401,
            )
        except jwt.InvalidTokenError:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid token",
                    "error": "401",
                },
                status=401,
            )
        user = User.objects.get(id=uid)
        return JsonResponse(
            {
                "success": True,
                "message": "User retrieved successfully",
                "user": user.toJSON(),
            },
            status=200,
        )


def edit_profile(request):
    if request.method == "POST":
        try:
            DATA = json.loads(request.body)
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid JSON, maybe data is not in JSON format",
                    "error": "400",
                },
                status=400,
            )

        try:
            token = request.headers.get("Authorization").split(" ")[1]
            uid = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])["uid"]
            user = User.objects.get(id=uid)
        except jwt.ExpiredSignatureError:
            return JsonResponse(
                {"success": False, "message": "Token expired", "error": "401"},
                status=401,
            )
        except jwt.InvalidTokenError:
            return JsonResponse(
                {"success": False, "message": "Invalid token", "error": "401"},
                status=401,
            )
        except KeyError:
            return JsonResponse(
                {"success": False, "message": "Missing token", "error": "400"},
                status=400,
            )

        if "password" not in DATA or not user.checkPassword(password):
            return JsonResponse(
                {"success": False, "message": "Invalid password", "error": "401"},
                status=401,
            )

        user.username = DATA["username"] if "username" in DATA else user.username
        user.email = DATA["email"] if "email" in DATA else user.email
        user.phone = DATA["phone"] if "phone" in DATA else user.phone
        user.first_name = (
            DATA["first_name"] if "first_name" in DATA else user.first_name
        )
        user.last_name = DATA["last_name"] if "last_name" in DATA else user.last_name
        if "new_password" in DATA:
            user.password = hashlib.sha256(
                DATA["new_password"].encode("utf-8")
            ).hexdigest()

        user.save()

        return JsonResponse(
            {
                "success": True,
                "message": "User updated successfully",
                "user": user.toJSON(),
            },
            status=200,
        )

    else:  # not a POST request
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request method",
                "error": "400",
            },
            status=400,
        )


def set_avatar(request):
    if request.method == "POST":
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            uid = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])["uid"]
            user = User.objects.get(id=uid)
        except jwt.ExpiredSignatureError:
            return JsonResponse(
                {"success": False, "message": "Token expired", "error": "401"},
                status=401,
            )
        except jwt.InvalidTokenError:
            return JsonResponse(
                {"success": False, "message": "Invalid token", "error": "401"},
                status=401,
            )
        except KeyError:
            return JsonResponse(
                {"success": False, "message": "Missing token", "error": "400"},
                status=400,
            )

        try:
            avatar = request.FILES["avatar"]
        except KeyError:
            return JsonResponse(
                {"success": False, "message": "Missing avatar", "error": "400"},
                status=400,
            )

        if avatar.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
            return JsonResponse(
                {"success": False, "message": "Invalid avatar", "error": "400"},
                status=400,
            )

        if avatar.size > 1000000:
            return JsonResponse(
                {"success": False, "message": "Avatar too large", "error": "400"},
                status=400,
            )

        avatar.name = str(user.id) + "." + avatar.name.split(".")[-1]
        user.avatar = avatar
        user.save()

        return JsonResponse(
            {
                "success": True,
                "message": "Avatar updated successfully",
                "user": user.toJSON(),
            },
            status=200,
        )

    else:  # not a POST request
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request",
                "error": "400",
            },
            status=400,
        )


def search_user(request):
    if request.method == "GET":
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            uid = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])["uid"]
            user = User.objects.get(id=uid)
        except jwt.ExpiredSignatureError:
            return JsonResponse(
                {"success": False, "message": "Token expired", "error": "401"},
                status=401,
            )
        except jwt.InvalidTokenError:
            return JsonResponse(
                {"success": False, "message": "Invalid token", "error": "401"},
                status=401,
            )
        except Exception:
            return JsonResponse(
                {"success": False, "message": "Missing token", "error": "400"},
                status=400,
            )

        try:
            q = request.GET["q"]
        except KeyError:
            return JsonResponse(
                {"success": False, "message": "Missing q", "error": "400"},
                status=400,
            )

        users = User.objects.filter(
            Q(is_active=True) & Q(username__icontains=q)
            | Q(email__icontains=q)
            | Q(phone__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(id__icontains=q)
        )
        users = users.exclude(id=user.id)

        return JsonResponse(
            {
                "success": True,
                "message": "Users found",
                "users": [user.toJSON() for user in users],
            },
            status=200,
        )

    else:  # not a GET request
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request method",
                "error": "400",
            },
            status=400,
        )
