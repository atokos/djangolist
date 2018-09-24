from django.db import models
from django.contrib.auth.models import User
import datetime

class Auction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    deadline = models.DateTimeField(default=datetime.datetime.now()+datetime.timedelta(hours=72))
