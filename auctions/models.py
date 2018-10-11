from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class AuctionManager(models.Manager):

    def get_all_active(self):
        return self.filter(banned=False, due=False)

    def get_by_id(self, auction_id):
        return self.get(pk=auction_id)

    def get_by_title(self, title):
        return self.filter(title__icontains=title, banned=False,
                           due=False).order_by('deadline')

    def exists(self, auction_id):
        return len(self.filter(pk=auction_id)) > 0


class Auction(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    seller = models.ForeignKey(User, related_name='auction-seller+',
                               default=None, on_delete=models.CASCADE)
    minimum_bid = models.DecimalField(max_digits=8, decimal_places=2)
    deadline = models.DateTimeField()

    banned = models.BooleanField(default=False)
    due = models.BooleanField(default=False)

    current_bidder = models.ForeignKey(User, related_name='auction-bidder+',
                                       default=None, on_delete=models.SET_DEFAULT)
    current_bid = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    bidders = models.ManyToManyField(User, blank=True)

    objects = AuctionManager()

    def __str__(self):
        return self.title

    def is_due(self):
        return self.due

    def is_active(self):
        return not self.banned and not self.due

    def set_latest_bidder(self, new_bidder):
        old_bidder = self.latest_bidder
        self.latest_bidder = new_bidder
        return old_bidder

    # def check_deadline(self, time):
    #    if (self.deadline - time) <= timezone.timedelta(minutes=5):
    #        self.deadline += timezone.timedelta(minutes=5)


