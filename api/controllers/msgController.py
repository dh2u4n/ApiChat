from api.models.user import User
from api.models.message import Message, FileMessage
from api.models.group import Group
from api.models.couple import Couple
from api.models.room import Room

from django.http import JsonResponse
from ApiChat.settings import SECRET_KEY, HOST_URL


import jwt  # pip install PyJWT
import hashlib
import json
import datetime


def get_recent_messages(request):
    if request.method == "GET":
        try:
            token = request.META.get("HTTP_AUTHORIZATION").split(" ")[1]
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
            if item.last_message:
                res.append(
                    {
                        "room_id": item.id,
                        "room_type": "group",
                        "name": item.name,
                        "avatar": HOST_URL + item.avatar.url if item.avatar else None,
                        "last_message": item.last_message.toJSON(),
                    }
                )
        for item in Couple.objects.filter(user1=user):
            if item.last_message and item.user1_accepted:
                res.append(
                    {
                        "room_id": item.id,
                        "room_type": "couple",
                        "name": item.nickname2 or item.user2.full_name,
                        "avatar": HOST_URL + item.user2.avatar.url
                        if item.user2.avatar
                        else None,
                        "last_message": item.last_message.toJSON(),
                    }
                )
        for item in Couple.objects.filter(user2=user):
            if item.user1 == item.user2:
                continue
            if item.last_message and item.user2_accepted:
                res.append(
                    {
                        "room_id": item.id,
                        "room_type": "couple",
                        "name": item.nickname1 or item.user1.full_name,
                        "avatar": HOST_URL + item.user1.avatar.url
                        if item.user1.avatar
                        else None,
                        "last_message": item.last_message.toJSON(),
                    }
                )

        return JsonResponse(
            {
                "success": True,
                "message": "Recent messages",
                "data": sorted(
                    res, key=lambda x: x["last_message"]["created_at"], reverse=True
                ),
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


def send_message(request):
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
        try:  # try checking room_id is a group_id
            room_id = int(DATA["room_id"])
            user.groups.get(id=room_id)
        except:  # room_id is not a group_id
            try:  # try checking room_id is a couple_id
                couple = Couple.objects.get(id=room_id)
                user2 = couple.user2 if user == couple.user1 else couple.user1
                if user not in [couple.user1, couple.user2]:
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "Invalid room id",
                            "error": 400,
                        },
                        status=400,
                    )
            except:  # room_id is not a couple_id and is not a group_id
                try:  # try checking room_id is a user_id
                    user2 = User.objects.get(id=room_id)
                    try:  # try getting a couple with user and user2
                        couple = Couple.objects.get(user1=user, user2=user2)
                        room_id = couple.id
                    except:  # couple does not exist with user and user2
                        try:  # find the couple again with user2 and user(reverse) :)
                            couple = Couple.objects.get(user1=user2, user2=user)
                            room_id = couple.id
                        except:  # if both cases failed, then no couple exists, so create one
                            new_couple = Couple.objects.create(
                                user1=user,
                                user2=user2,
                                user1_accepted=True,  # user1 accepted because he is the sender
                            )

                            while (
                                new_couple.id % 2 == 0
                            ):  # make sure the couple/group id is odd
                                new_couple.delete()
                                new_couple.id += 1
                                new_couple.save()

                            room_id = new_couple.id

                except:  # room_id is not a user_id
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "Invalid room id",
                            "error": 400,
                        },
                        status=400,
                    )

        reply_to = None
        if "reply_to" in DATA:
            try:
                reply_to = Message.objects.get(id=DATA["reply_to"], room=room_id)
            except:
                try:
                    new_couple.delete()
                except:
                    pass
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Invalid reply_to",
                        "error": 400,
                    },
                    status=400,
                )

        try:

            text = DATA["text"] if "text" in DATA else None
            num_of_files = len(FILES)

            if not text and not num_of_files:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Message cannot be empty",
                        "error": 400,
                    },
                    status=400,
                )

            msg = Message.objects.create(
                sender=user,
                room=Room.objects.get(id=room_id),
                text=text,
                reply_to=reply_to,
            )
            for i in range(1, num_of_files + 1):
                file = FILES[f"file{i}"]
                file.name = f"{user.id}_{room_id}.{file.name.split('.')[-1].lower()}"
                msg.files.create(file=file)
            msg.save()

            try:
                Couple.objects.get(id=room_id).accept(user)
            except:
                pass

            return JsonResponse(
                {
                    "success": True,
                    "message": msg.toJSON(),
                    "recipients": get_recipients(msg),
                },
                status=200,
            )
        except:
            try:
                new_couple.delete()
            except:
                pass
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
            r = msg.reactions.get(user=user)
            if reaction == None:
                r.delete()
            else:
                r.reaction = reaction
                r.save()
        except:  # reaction has not been created
            try:  # reaction has not been created
                couple = Couple.objects.get(id=msg.room.id)
                list_users = [couple.user1, couple.user2]
            except:
                try:
                    list_users = Group.objects.get(id=msg.room.id).members.all()
                except:
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "You are not a member of this room",
                            "error": 400,
                        },
                        status=400,
                    )

            if user not in list_users:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "You are not a member of this room",
                        "error": 400,
                    },
                    status=400,
                )
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

        return JsonResponse(
            {
                "success": True,
                "message": "Reaction sent",
            },
        )

    else:  # request.method != "POST"
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid method",
                "error": 405,
            },
            status=405,
        )


def get_messages(request):
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

        try:
            room_id = request.GET["room_id"]
            page = int(request.GET.get("page", 0))
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid data",
                    "error": 400,
                },
                status=400,
            )

        try:  # room exists
            room = Room.objects.get(id=room_id)
        except:  # room does not exist
            try:  # room_id is user_id
                user2 = User.objects.get(id=room_id)
                try:
                    room = Couple.objects.get(user1=user, user2=user2)
                    room_id = room.id
                except:
                    try:
                        room = Couple.objects.get(user1=user2, user2=user)
                        room_id = room.id
                    except:
                        return JsonResponse(
                            {
                                "success": False,
                                "message": "Does not exist any message in this room",
                                "error": 400,
                            },
                            status=400,
                        )
            except:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Invalid room_id",
                        "error": 400,
                    },
                    status=400,
                )

        try:
            couple = Couple.objects.get(id=room_id)
            if user not in [couple.user1, couple.user2]:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "You are not a member of this room",
                        "error": 400,
                    },
                    status=400,
                )
        except:
            group = Group.objects.get(id=room_id)
            if user not in group.members.all():
                return JsonResponse(
                    {
                        "success": False,
                        "message": "You are not a member of this room",
                        "error": 400,
                    },
                    status=400,
                )

        messages = Message.objects.filter(room=room).order_by("created_at")
        MESSAGES_PER_PAGE = 20
        num_all_messages = len(messages)

        if page * MESSAGES_PER_PAGE > num_all_messages:
            return JsonResponse(
                {
                    "success": False,
                    "message": "I have given you all the messages that I have. Now let me sleep. OK?",
                    "error": 400,
                },
                status=400,
            )

        # page begins at 0
        begin_index = max(0, num_all_messages - MESSAGES_PER_PAGE * (page + 1))
        end_index = num_all_messages - MESSAGES_PER_PAGE * page
        messages = messages[begin_index:end_index]

        return JsonResponse(
            {
                "success": True,
                "message": "Messages retrieved",
                "messages": [message.toJSON() for message in messages],
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


def get_pending_messages(request):
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

        for couple in Couple.objects.filter(user2=user):
            if couple.last_message and not couple.user2_accepted:
                res.append(
                    {
                        "room_id": couple.id,
                        "room_type": "couple",
                        "name": couple.nickname1 or couple.user1.full_name,
                        "avatar": HOST_URL + couple.user1.avatar.url
                        if couple.user1.avatar
                        else None,
                        "last_message": couple.last_message.toJSON(),
                    }
                )

        return JsonResponse(
            {
                "success": True,
                "message": "Recent messages",
                "data": sorted(
                    res, key=lambda x: x["last_message"]["created_at"], reverse=True
                ),
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


def get_recipients(msg):
    try:
        couple = Couple.objects.get(id=msg.room.id)
        return [couple.user1.id, couple.user2.id]
    except:
        group = Group.objects.get(id=msg.room.id)
        return [member.id for member in group.members.all()]
