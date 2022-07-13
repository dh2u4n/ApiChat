# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer

from api.models.user import User
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
        await self.channel_layer.group_discard(self.room_id, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if text_data_json["type"] == "join_room":
            await self.join_room(text_data_json["room_id"])

        elif text_data_json["type"] == "send_message":
            print(text_data_json)
            await self.channel_layer.group_send(
                self.room_id,
                {"type": "send_message", "message": text_data_json["message"]},
            )
        else:
            print("Unknown event type")
            await self.channel_layer.group_send(
                "1758374927612", {"type": "notification_message", "message": "Hello"}
            )

    async def notification_message(self, event):
        await self.send(
            text_data=json.dumps(
                {"type": "notification_message", "message": event["message"]}
            )
        )

    async def send_message(self, event):
        await self.send(
            text_data=json.dumps({"type": "send_message", "message": event["message"]})
        )

    async def join_room(self, room_id):
        await self.channel_layer.group_discard(self.uid, self.channel_name)
        self.room_id = room_id
        await self.channel_layer.group_add(self.room_id, self.channel_name)
