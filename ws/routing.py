# chat/routing.py
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/notification/<str:token>/", consumers.NotificationConsumer.as_asgi()),
]
