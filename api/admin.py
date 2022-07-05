from django.contrib import admin

from api.models.user import User
from api.models.message import Message, FileMessage
from api.models.room import Room
from api.models.group import Group
from api.models.couple import Couple
from api.models.reaction import Reaction

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "full_name", "avatar", "is_active")
    list_display_links = ("id", "username", "email")
    list_filter = ("is_active",)
    search_fields = ("username", "email", "full_name")


class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "text", "room", "reply_to", "created_at", "deleted")
    list_filter = ("sender", "room")
    search_fields = ("text",)


class FileMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "file")
    list_filter = ("message",)
    search_fields = ("file",)


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
    list_display = ("id", "user1", "user2", "user1_accepted", "user2_accepted")
    list_filter = ("user1", "user2")
    search_fields = ("user1", "user2")


admin.site.register(User, UserAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(FileMessage, FileMessageAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Couple, CoupleAdmin)
admin.site.register(Reaction)
