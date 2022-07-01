from django.db import models

from api.models.message import Message

class Room(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "rooms"

    # last_message
    @property
    def last_message(self):
        return Message.objects.filter(room=self).order_by("-created_at").first()

    def __str__(self):
        return str(self.id)

    def toJSON(self):
        return {
            "id": self.id,
        }