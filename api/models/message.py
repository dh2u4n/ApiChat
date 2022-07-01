from django.db import models

from ApiChat.settings import HOST_URL

from api.models.user import User


class Message(models.Model):
    type_choices = (
        ("text", "Văn bản"),
        ("image", "Hình ảnh"),
        ("video", "Video"),
        ("audio", "Âm thanh"),
        ("file", "Tệp"),
    )

    type = models.CharField(max_length=10, choices=type_choices)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="m/images/", blank=True, null=True)
    video = models.FileField(upload_to="m/videos/", blank=True, null=True)
    audio = models.FileField(upload_to="m/audios/", blank=True, null=True)
    file = models.FileField(upload_to="m/files/", blank=True, null=True)

    reply_to = models.ForeignKey("Message", on_delete=models.CASCADE, related_name="replies", null=True, blank=True)
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
            "type": self.type,
            "text": self.text,
            "image": HOST_URL + self.image.url if self.image else None,
            "video": HOST_URL + self.video.url if self.video else None,
            "audio": HOST_URL + self.audio.url if self.audio else None,
            "file": HOST_URL + self.file.url if self.file else None,
            "reaction": [reaction.toJSON() for reaction in self.reactions.all()],
            "sender": {
                "name": self.sender.first_name,
                "avatar": self.sender.avatar.url
            },
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
