from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta


class Auction(models.Model):
    STATE_CHOICES = (('ACTIVE', 'ACTIVE'),
                     ('BANNED', 'BANNED'),
                     ('DUE', 'DUE'),
                     ('ADJUDICATED', 'ADJUDICATED'),
                     )
    user = models.ForeignKey(User, related_name='auction-seller+', default=None, on_delete=models.CASCADE)
    latest_bidder = models.ForeignKey(User, related_name='auction-bidder+', default=None, null=True, on_delete=models.SET_DEFAULT)
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    deadline = models.DateTimeField()
    state = models.CharField(max_length=12, choices=STATE_CHOICES, default='ACTIVE')

    def __str__(self):
        return self.title

    def short_desc(self):
        return self.description[:500]

    def set_latest_bidder(self, new_bidder):
        old_bidder = self.latest_bidder
        self.latest_bidder = new_bidder
        return old_bidder

    def check_deadline(self, time):
        if (self.deadline - time) <= timedelta(minutes=5):
            self.deadline += timedelta(minutes=5)
