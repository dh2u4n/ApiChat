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
        token = self.scope["url_route"]["kwargs"]["token"]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = await sync_to_async(User.objects.get)(id=payload["uid"])
            self.uid = str(user.id)
            await self.channel_layer.group_add(self.uid, self.channel_name)

            await self.channel_layer.group_send(
                self.uid, {"type": "notification_message", "message": "Hello"}
            )

            await self.accept()
        except:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.uid, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if "add_member" in text_data_json:
            room_id = text_data_json["add_member"]["room_id"]
            user_id = text_data_json["add_member"]["user_id"]
            await self.channel_layer.group_send(
                str(user_id), {"type": "add_member", "room_id": room_id}
            )
        else:
            message = text_data_json["message"]
            recipients = text_data_json["recipients"]

            for recipient in recipients:
                await self.channel_layer.group_send(
                    str(recipient), {"type": "notification_message", "message": message}
                )

    async def notification_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    async def add_member(self, event):
        await self.send(text_data=json.dumps(event))
