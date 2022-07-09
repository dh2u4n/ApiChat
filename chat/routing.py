# chat/routing.py
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/notificatiob/<str:token>/", consumers.NotificationConsumer.as_asgi()),
    path("ws/room/<str:room_id>/<str:token>/", consumers.ChatConsumer.as_asgi()),
]
