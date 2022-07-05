from django.db import models

import hashlib
from ApiChat.settings import HOST_URL

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    avatar = models.ImageField(upload_to="u/avatars/", null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.first_name + " " + self.last_name + " (" + self.username + ")"

    def toJSON(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "avatar": HOST_URL + self.avatar.url if self.avatar else None,
            "joined_at": self.joined_at,
            "last_login": self.last_login,
            "is_active": self.is_active,
        }

    def checkPassword(self, password):
        return self.password == hashlib.sha256(password.encode("utf-8")).hexdigest()

    @property
    def full_name(self):
        return self.last_name + " " + self.first_name