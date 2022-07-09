# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer

from api.models.user import User
from ApiChat.settings import SECRET_KEY

import json
import jwt



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        token = self.scope["url_route"]["kwargs"]["token"]
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        # self.channel_name = token
        # Join room group
        await self.channel_layer.group_add(self.room_id, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_id, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_id, {"type": "send_message", "message": text_data}
        )

    # Receive message from room group
    async def send_message(self, event):
        message = event["message"]
        # Send message to WebSocket
        await self.send(text_data=message)


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        token = self.scope["url_route"]["kwargs"]["token"]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["uid"])
            self.user = user
            self.channel_name = "notification_" + str(user.id)
            await self.channel_layer.group_add(self.channel_name, self.channel_name)
            await self.accept()
        except Exception as e:
            print(e)
            await self.close()
            

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.channel_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender = data["sender"]
        
        await self.channel_layer.group_send(
            self.channel_name, {"type": "send_message", "message": text_data}
        )

    async def send_message(self, event):
        message = event["message"]
        await self.send(text_data=message)