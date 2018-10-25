from django.db import models
from django.contrib.auth.models import User


class UserPreference(models.Model):
    language = models.CharField(max_length=10, default='en')
    user = models.OneToOneField(User, default=None, on_delete=models.CASCADE)
