from django.db import models

from ApiChat.settings import HOST_URL

from api.models.room import Room


class Group(Room):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField("User", related_name="groups")
    owner = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="owned_groups"
    )
    members_can_change_info = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to="g/", null=True, blank=True)

    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "groups"

    def __str__(self):
        return self.name

    def toJSON(self):
        return {
            "id": self.id,
            "name": self.name,
            "owner": self.owner.id,
            "members": [member.toJSON() for member in self.members.all()],
            "avatar": HOST_URL + self.avatar.url if self.avatar else None,
            "last_message": self.last_message.toJSON() if self.last_message else None,
        }
