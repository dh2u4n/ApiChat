# chat/routing.py
from django.urls import path

from . import consumers
from . import consumers2

websocket_urlpatterns = [
    path("ws/notification/<str:token>/", consumers.NotificationConsumer.as_asgi()),
    # path("ws/notification/", consumers2.NotificationConsumer.as_asgi()),
]
