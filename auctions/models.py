from django.db import models
from django.contrib.auth.models import User


class Auction(models.Model):

    ACTIVE = 'ACTIVE'
    BANNED = 'BANNED'
    DUE = 'DUE'
    ADJUDICATED = 'ADJUDICATED'
    STATE_CHOICES = ((ACTIVE, 'ACTIVE'),
                     (BANNED, 'BANNED'),
                     (DUE, 'DUE'),
                     (ADJUDICATED, 'ADJUDICATED'),
                     )

    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    deadline = models.DateTimeField()
    state = models.CharField(max_length=12, choices=STATE_CHOICES, default=ACTIVE)

    def __str__(self):
        return self.title

    def short_desc(self):
        return self.description[:500]
