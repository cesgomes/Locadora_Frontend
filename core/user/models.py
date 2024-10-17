from django.db import models
from django.utils import timezone


class RegistrationToken(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True)
    expiration = models.DateTimeField()

    def is_valid(self):
        return self.expiration >= timezone.now()

    def __str__(self):
        return self.email
