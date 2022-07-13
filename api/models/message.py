from django.db import models

from ApiChat.settings import HOST_URL

from api.models.user import User


class Message(models.Model):
    text = models.TextField(blank=True, null=True)
    reply_to = models.ForeignKey(
        "Message",
        on_delete=models.CASCADE,
        related_name="replies",
        null=True,
        blank=True,
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    room = models.ForeignKey("Room", on_delete=models.CASCADE, related_name="messages")
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "messages"

    def __str__(self):
        return str(self.id) + " - " + self.sender.full_name + " -> " + str(self.room.id)

    def toJSON(self):
        return {
            "id": self.id,
            "text": self.text,
            "files": [file.file.url for file in self.files.all()],
            "reply_to": {
                "sender": {
                    "id": self.reply_to.sender.id,
                    "first_name": self.reply_to.sender.first_name,
                    "last_name": self.reply_to.sender.last_name,
                },
                "text": self.reply_to.text,
                "files": [file.file.url for file in self.reply_to.files.all()],
            }
            if self.reply_to
            else None,
            "reaction": [reaction.toJSON() for reaction in self.reactions.all()],
            "sender": {
                "id": self.sender.id,
                "first_name": self.sender.first_name,
                "last_name": self.sender.last_name,
                "avatar": self.sender.avatar.url if self.sender.avatar else None,
            },
            "room": self.room.id,
            "created_at": self.created_at,
        }


class FileMessage(models.Model):
    file = models.FileField(upload_to="m/files/")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="files")

    class Meta:
        db_table = "file_messages"

    def __str__(self):
        return (
            str(self.id)
            + " - "
            + self.message.sender.full_name
            + " -> "
            + str(self.message.room.id)
        )

    def toJSON(self):
        return {
            "file": HOST_URL + self.file.url,
        }
