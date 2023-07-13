# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from api.models.user import User
from api.models.group import Group
from api.models.couple import Couple
from ApiChat.settings import SECRET_KEY

import json
import jwt
from asgiref.sync import sync_to_async


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        try:
            self.uid = None
            await self.accept()
        except:
            await self.close()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.uid, self.channel_name)
        except:
            pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if "auth" in text_data_json:
            token = text_data_json["auth"]["token"]
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            try:
                user = await sync_to_async(User.objects.get)(id=payload["uid"])
            except:
                await self.close()
                return
            self.uid = str(user.id)
            await self.channel_layer.group_add(self.uid, self.channel_name)
            await self.send(text_data=json.dumps({"auth": "success"}))
            await self.channel_layer.group_send(
                self.uid, {"type": "add_member", "message": "hello", "uid": self.uid}
            )

        elif not self.uid:
            await self.close()
            return

        if "add_member" in text_data_json:
            room_id = text_data_json["add_member"]["room_id"]
            user_id = text_data_json["add_member"]["user_id"]
            await self.channel_layer.group_send(
                str(user_id), {"type": "add_member", "room_id": room_id}
            )
        elif "message" in text_data_json:
            message = text_data_json["message"]
            recipients = text_data_json["recipients"]

            for recipient in recipients:
                await self.channel_layer.group_send(
                    str(recipient), {"type": "notification_message", "message": message}
                )

    async def notification_message(self, event):
        await self.send(text_data=event["message"])

    async def add_member(self, event):
        await self.send(text_data=json.dumps(event))
