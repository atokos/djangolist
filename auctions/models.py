from django.db import models
from django.contrib.auth.models import User
import datetime


class Auction(models.Model):
    # TODO user field later when user accounts exist
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    # TODO require min 72h from now
    deadline = models.DateTimeField(default=datetime.datetime.now() + datetime.timedelta(hours=72))

    def __str__(self):
        return self.title

    def short_desc(self):
        return self.description[:500]
