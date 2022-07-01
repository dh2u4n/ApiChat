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


def get_recent_messages(request):
    if request.method == "GET":
        try:
            token = request.headers["Authorization"].split(" ")[1]
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

        res = []

        for item in user.groups.all():
            res.append(
                {
                    "room_id": item.id,
                    "room_type": "group",
                    "name": item.name,
                    "last_message": item.last_message.toJSON(),
                }
            )
        for item in Couple.objects.filter(user1=user):
            res.append(
                {
                    "room_id": item.id,
                    "room_type": "couple",
                    "name": item.nickname2 or item.user2.full_name,
                    "last_message": item.last_message.toJSON(),
                }
            )
        for item in Couple.objects.filter(user2=user):
            res.append(
                {
                    "room_id": item.id,
                    "room_type": "couple",
                    "name": item.nickname1 or item.user1.full_name,
                    "last_message": item.last_message.toJSON(),
                }
            )

        return JsonResponse(
            {
                "success": True,
                "message": "Recent messages",
                "data": sorted(res, key=lambda x: x["last_message"]["created_at"]),
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


def add_new_message(request):
    if request.method == "POST":
        try:
            token = request.headers["Authorization"].split(" ")[1]
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

        DATA = request.POST.copy()
        FILES = request.FILES.copy()
        try:
            room_id = int(DATA["room_id"])
            user.groups.get(id=room_id)
        except:
            try:
                couple = Couple.objects.get(id=room_id)
                if user not in [couple.user1, couple.user2]:
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "Invalid room id",
                            "error": 400,
                        },
                        status=400,
                    )
                if not Message.objects.filter(room=couple, sender=user).exists():
                    # accept the couple
                    couple.is_pending = False
                    couple.save()
            except:
                try:
                    user2 = User.objects.get(id=room_id)
                    is_pending = user != user2
                    Couple.objects.create(
                        user1=user, user2=user2, is_pending=is_pending
                    )
                except:
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "Invalid room id",
                            "error": 400,
                        },
                        status=400,
                    )

        try:
            msg_type = DATA["type"]
            if msg_type not in ["text", "image", "video", "audio", "file"]:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Message type must be one of text, image, video, audio, file",
                        "error": 400,
                    },
                    status=400,
                )
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Message type is required in data",
                    "error": 400,
                },
                status=400,
            )

        reply_to = None
        if "reply_to" in DATA:
            try:
                reply_to = Message.objects.get(id=DATA["reply_to"], room=room_id)
            except:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Invalid reply_to",
                        "error": 400,
                    },
                    status=400,
                )

        try:
            msg_text = None
            msg_image = None
            msg_video = None
            msg_audio = None
            msg_file = None
            if msg_type == "text":
                msg_text = DATA["text"]
            elif msg_type == "image":
                msg_image = FILES["image"]
            elif msg_type == "video":
                msg_video = FILES["video"]
            elif msg_type == "audio":
                msg_audio = FILES["audio"]
            elif msg_type == "file":
                msg_file = FILES["file"]

            Message.objects.create(
                sender=user,
                room=Room.objects.get(id=room_id),
                type=msg_type,
                text=msg_text,
                reply_to=reply_to,
                image=msg_image,
                video=msg_video,
                audio=msg_audio,
                file=msg_file,
            )

            return JsonResponse(
                {
                    "success": True,
                    "message": "Message sent",
                },
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

    else:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid method",
                "error": 405,
            },
            status=405,
        )


def react_to_message(request):
    if request.method == "POST":
        try:
            token = request.headers["Authorization"].split(" ")[1]
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
            msg = Message.objects.get(id=DATA["message_id"])
            reaction = DATA["reaction"]
            if reaction not in [
                "like",
                "dislike",
                "love",
                "haha",
                "wow",
                "sad",
                "angry",
                None,
            ]:
                raise Exception("Invalid reaction")
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid data",
                    "error": 400,
                },
                status=400,
            )

        try:  # reaction has already been created
            msg.reactions.get(user=user)
            if reaction == None:
                msg.reactions.get(user=user).delete()
            else:
                msg.reactions.get(user=user).update(reaction=reaction)
        except:
            try:  # reaction has not been created
                if (
                    user in Couple.objects.get(id=msg.room.id).users.all()
                    or user in Group.objects.get(id=msg.room.id).members
                ):
                    if reaction:  # reaction is not None
                        msg.reactions.create(user=user, reaction=reaction)
                    else:  # can't create a reaction with None
                        return JsonResponse(
                            {
                                "success": False,
                                "message": "Cannot create a reaction with None",
                                "error": 400,
                            },
                            status=400,
                        )
                else:
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "You are not a member of this room",
                            "error": 400,
                        },
                        status=400,
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

        return JsonResponse(
            {
                "success": True,
                "message": "Reaction sent",
            },
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
