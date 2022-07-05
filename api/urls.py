from django.urls import path

from . import views
from api.controllers import userController
from api.controllers import msgController
from api.controllers import groupController

urlpatterns = [
    path("docs", views.docs),
    path("test", views.test),

    path("register", userController.register),
    path("login", userController.login),
    path("get_profile", userController.get_profile),
    path("edit_profile", userController.edit_profile),
    path("set_avatar", userController.set_avatar),
    path("search_user", userController.search_user),

    path("get_recent_messages", msgController.get_recent_messages),
    path("get_pending_messages", msgController.get_pending_messages),
    path("get_messages", msgController.get_messages),
    path("send_message", msgController.send_message),
    path("react_to_message", msgController.react_to_message),

    path("create_group", groupController.create_group),
    path("add_user_to_group", groupController.add_user_to_group),
    path("group_settings", groupController.group_settings),
    path("remove_user_from_group", groupController.remove_user_from_group),
    path("delete_group", groupController.delete_group),

]
