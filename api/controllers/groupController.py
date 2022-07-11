from api.models.user import User
from api.models.message import Message
from api.models.group import Group
from api.models.couple import Couple
from api.models.room import Room

from django.http import JsonResponse
from ApiChat.settings import SECRET_KEY

import jwt  # pip install PyJWT
import hashlib
import json
import datetime


def create_group(request):
    if request.method == "POST":
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            uid = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])["uid"]
            user = User.objects.get(id=uid)
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid token",
                    "error": 401,
                },
                status=401,
            )

        try:
            DATA = request.POST
            name = DATA["name"]
            members_can_change_info = (
                DATA["members_can_change_info"] == 1
                if "members_can_change_info" in DATA
                else False
            )
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid data",
                    "error": 400,
                },
                status=400,
            )

        try:
            group = Group.objects.create(
                name=name,
                owner=user,
                members_can_change_info=members_can_change_info,
            )

            while group.id % 2 == 0:
                group.delete()
                group.id += 1
                group.save()

            if "avatar" in request.FILES:
                avatar = request.FILES["avatar"]
                if avatar.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
                    group.delete()
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "Avatar must be a jpeg, jpg or png",
                            "error": 400,
                        },
                        status=400,
                    )
                avatar.name = "g_" + str(group.id) + "." + avatar.name.split(".")[-1]
                group.avatar = avatar

            group.members.add(user)
            Message.objects.create(
                sender=user,
                text="Welcome to the group!",
                room=group,
            )

            group.save()
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid data",
                    "error": 400,
                },
                status=400,
            )

        return JsonResponse(
            {
                "success": True,
                "message": "Group created",
                "group": group.toJSON(),
            },
            status=200,
        )

    else:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid method",
                "error": 405,
            },
            status=405,
        )


def add_user_to_group(request):
    if request.method == "POST":
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            uid = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])["uid"]
            user = User.objects.get(id=uid)
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid token",
                    "error": 401,
                },
                status=401,
            )

        try:
            DATA = json.loads(request.body)
            group = Group.objects.get(id=DATA["group_id"])
            other_user = User.objects.get(id=DATA["user_id"])
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid data",
                    "error": 400,
                },
                status=400,
            )

        if user == group.owner or group.members_can_change_info:
            if other_user not in group.members.all():
                group.members.add(other_user)
                return JsonResponse(
                    {
                        "success": True,
                        "message": "User added to group",
                        # "group": group.toJSON(),
                    },
                    status=200,
                )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "User already in group",
                        # "group": group.toJSON(),
                    },
                    status=400,
                )
        else:  # user does not have permission to add other user to group
            return JsonResponse(
                {
                    "success": False,
                    "message": "You do not have permission to add users to this group",
                    # "group": group.toJSON(),
                },
                status=400,
            )

    else:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid method",
                "error": 405,
            },
            status=405,
        )


def group_settings(request):
    if request.method == "POST":
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            uid = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])["uid"]
            user = User.objects.get(id=uid)
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid token",
                    "error": 401,
                },
                status=401,
            )

        try:
            DATA = request.POST
            FILES = request.FILES
            group = Group.objects.get(id=DATA["group_id"])
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid data",
                    "error": 400,
                },
                status=400,
            )

        if "members_can_change_info" in DATA:
            if user == group.owner:
                group.members_can_change_info = DATA["members_can_change_info"] == 1
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "You do not have permission to do this",
                        # "group": group.toJSON(),
                    },
                    status=400,
                )

        group.name = DATA["name"] if "name" in DATA else group.name
        avatar = FILES["avatar"] if "avatar" in FILES else group.avatar
        avatar.name = "g_" + str(group.id) + "." + avatar.name.split(".")[-1]
        group.avatar = avatar

        group.save()

        return JsonResponse(
            {
                "success": True,
                "message": "Group settings updated",
                "group": group.toJSON(),
            },
            status=200,
        )

    else:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid method",
                "error": 405,
            },
            status=405,
        )


def remove_user_from_group(request):
    if request.method == "POST":
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            uid = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])["uid"]
            user = User.objects.get(id=uid)
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid token",
                    "error": 401,
                },
                status=401,
            )

        try:
            DATA = json.loads(request.body)
            group = Group.objects.get(id=DATA["group_id"])
            other_user = User.objects.get(id=DATA["user_id"])
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid data",
                    "error": 400,
                },
                status=400,
            )

        if user != group.owner:
            return JsonResponse(
                {
                    "success": False,
                    "message": "You do not have permission to do this",
                },
                status=400,
            )

        if other_user in group.members.all():
            group.members.remove(other_user)
            return JsonResponse(
                {
                    "success": True,
                    "message": "User removed from group",
                },
                status=200,
            )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "User not in group",
                },
                status=400,
            )

    else:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid method",
                "error": 405,
            },
            status=405,
        )


def delete_group(request):
    if request.method == "POST":
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            uid = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])["uid"]
            user = User.objects.get(id=uid)
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid token",
                    "error": 401,
                },
                status=401,
            )

        try:
            DATA = json.loads(request.body)
            group = Group.objects.get(id=DATA["group_id"])
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid data",
                    "error": 400,
                },
                status=400,
            )

        if user != group.owner:
            return JsonResponse(
                {
                    "success": False,
                    "message": "You do not have permission to do this",
                },
                status=400,
            )

        group.deleted = True
        group.save()
        return JsonResponse(
            {
                "success": True,
                "message": "Group deleted",
            },
            status=200,
        )

    else:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid method",
                "error": 405,
            },
            status=405,
        )


def group_info(request):
    if request.method == "GET":
        try:
            token = request.headers.get("Authorization").split(" ")[1]
            uid = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])["uid"]
            user = User.objects.get(id=uid)
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid token",
                    "error": 401,
                },
                status=401,
            )

        try:
            DATA = request.GET
            group = user.groups.get(id=DATA["group_id"])
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid data",
                    "error": 400,
                },
                status=400,
            )

        return JsonResponse(
            {
                "success": True,
                "message": "Group info",
                "group": group.toJSON(),
            },
            status=200,
        )

    else:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid method",
                "error": 405,
            },
            status=405,
        )
