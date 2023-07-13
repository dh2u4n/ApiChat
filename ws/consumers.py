# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from api.models.user import User
from api.models.group import Group
from api.models.couple import Couple
from ApiChat.settings import SECRET_KEY, CHANNEL_LAYERS

import json
import jwt
from asgiref.sync import sync_to_async

# Add a new method to ChannelLayer
# We can send message to client with uid instead of channel_name
from django.utils.module_loading import import_string
async def send_by_uid(self, uid, message):
    try:
        for channel_name in self.uid_map[uid]:
            await self.send(channel_name, message)
    except:
        pass

ChannelLayer = import_string(CHANNEL_LAYERS["default"]["BACKEND"])
ChannelLayer.send_by_uid = send_by_uid


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        token = self.scope["url_route"]["kwargs"]["token"]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            self.uid = (await sync_to_async(User.objects.get)(id=payload["uid"])).id

            await self.channel_layer.group_add("system", self.channel_name)

            if hasattr(self.channel_layer, "uid_map"):
                self.channel_layer.uid_map[self.uid].add(self.channel_name) # multiple login from same user
            else:
                self.channel_layer.uid_map = {self.uid: {self.channel_name}}

            await self.accept()
        except:
            await self.close()

    async def disconnect(self, close_code):
        try:
            self.channel_layer.uid_map[self.uid].remove(self.channel_name)
            self.channel_layer.group_discard("system", self.channel_name)
        except:
            pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if "add_member" in text_data_json:
            room_id = text_data_json["add_member"]["room_id"]
            user_id = text_data_json["add_member"]["user_id"]
            # await self.send_to_user(
            await self.channel_layer.send_by_uid(
                user_id,
                {
                    "type": "add_member",
                    "room_id": room_id,
                },
            )

        elif "message" in text_data_json:
            message = text_data_json["message"]
            recipients = text_data_json["recipients"]

            for recipient in recipients:
                # await self.send_to_user(
                await self.channel_layer.send_by_uid(
                    recipient,
                    {
                        "type": "notification_message",
                        "message": message,
                    },
                )

        elif "kick_member" in text_data_json:
            room_id = text_data_json["kick_member"]["room_id"]
            user_id = text_data_json["kick_member"]["user_id"]
            # await self.send_to_user(
            await self.channel_layer.send_by_uid(
                user_id,
                {
                    "type": "kick_member",
                    "room_id": room_id,
                },
            )

        else:
            await self.channel_layer.group_send(
                "system",
                {
                    "type": "system_notification",
                    "message": text_data_json,
                },
            )

    async def system_notification(self, event):
        await self.send(text_data=json.dumps(event))

    async def notification_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    async def add_member(self, event):
        await self.send(text_data=json.dumps(event))

    async def kick_member(self, event):
        await self.send(text_data=json.dumps(event))

    # async def send_to_user(self, user_id, message):
    #     try:
    #         for channel_name in self.channel_layer.uid_map[user_id]:
    #             await self.channel_layer.send(channel_name, message)
    #     except:
    #         pass