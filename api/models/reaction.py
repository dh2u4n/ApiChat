from django.db import models

from api.models.user import User
from api.models.message import Message


class Reaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="reactions")
    reaction_choices = (
        ("like", "Like"),
        ("dislike", "Dislike"),
        ("love", "Love"),
        ("haha", "Haha"),
        ("wow", "Wow"),
        ("sad", "Sad"),
        ("angry", "Angry"),
    )
    reaction = models.CharField(max_length=10, choices=reaction_choices)

    class Meta:
        db_table = "reactions"

    def __str__(self):
        return self.user.full_name + " - " + self.reaction + " - " + str(self.message.id)

    def toJSON(self):
        return {
            "id": self.id,
            "user": self.user.id,
            "reaction": self.reaction,
        }