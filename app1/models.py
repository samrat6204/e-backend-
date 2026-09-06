from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    full_name = models.CharField(max_length=150)

    phone_number = models.CharField(
        max_length=20,
        unique=True
    )

    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
