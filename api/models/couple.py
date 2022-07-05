from django.db import models

from api.models.room import Room
from api.models.message import Message


class Couple(Room):
    user1 = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="+", null=False
    )
    user2 = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="+", null=False
    )
    nickname1 = models.CharField(max_length=50, blank=True, null=True)
    nickname2 = models.CharField(max_length=50, blank=True, null=True)

    user1_accepted = models.BooleanField(default=False)
    user2_accepted = models.BooleanField(default=False)

    class Meta:
        db_table = "couples"

    def __str__(self):
        return self.user1.full_name + " - " + self.user2.full_name

    def toJSON(self):
        return {
            "id": self.id,
            "user1": self.user1.id,
            "user2": self.user2.id,
            "nickname1": self.nickname1,
            "nickname2": self.nickname2,
            "last_message": self.last_message.toJSON() if self.last_message else None,
        }

    def checkAccept(self, user):
        if user == self.user1:
            return not self.user1_accepted
        elif user == self.user2:
            return not self.user2_accepted
        else:
            return False

    def accept(self, user):
        if user == self.user1:
            self.user1_accepted = True
        elif user == self.user2:
            self.user2_accepted = True
        else:
            return False
        self.save()
        return True