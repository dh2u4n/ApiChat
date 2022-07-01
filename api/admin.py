from django.contrib import admin

from api.models.user import User
from api.models.message import Message
from api.models.room import Room
from api.models.group import Group
from api.models.couple import Couple
from api.models.reaction import Reaction

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "avatar", "is_active")



class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sender",
        "room",
        "text",
        "image",
        "video",
        "audio",
        "file",
        "created_at",
    )
    list_filter = ("sender", "room")
    search_fields = ("text",)


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "members_can_change_info",
        "avatar",
        "created_at",
    )
    list_filter = ("owner", "members")
    search_fields = ("name",)


class CoupleAdmin(admin.ModelAdmin):
    list_display = ("id", "user1", "user2", "is_pending")
    list_filter = ("user1", "user2")
    search_fields = ("user1", "user2")






admin.site.register(User, UserAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Room)
admin.site.register(Group, GroupAdmin)
admin.site.register(Couple, CoupleAdmin)
admin.site.register(Reaction)
