from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from django.urls import reverse


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

    seller = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    minimum_bid = models.DecimalField(max_digits=8, decimal_places=2)
    deadline = models.DateTimeField()

    banned = models.BooleanField(default=False)
    due = models.BooleanField(default=False)
    #resolved = models.BooleanField(default=False)

    objects = AuctionManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('auctions:detail', args=[str(self.id)])

    def is_active(self):
        return not self.banned and not self.due

    def check_deadline(self):
        if self.deadline < timezone.now():
            self.due = True

    def get_latest_bid(self):
        if not self.bid_set.all():
            return None
        return self.bid_set.all().latest('created')

    def get_latest_bidder(self):
        if not self.bid_set.all():
            return None
        return self.get_latest_bid().bidder

    def get_latest_bid_amount(self):
        if not self.bid_set.all():
            return None
        return self.get_latest_bid().bid_amount


class Bid(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    auction = models.ForeignKey(Auction, default=None, on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.bidder.username + ': ' + str(self.bid_amount)
'''
    def clean_bid_amount(self):
        auction = self.auction
        if auction.get_latest_bid():
            if self.bid_amount < auction.get_latest_bid_amount() + Decimal('0.01'):
                raise ValidationError("The bid must be at least 0.01 higher than the current bid")
        if self.bid_amount < auction.minimum_bid:
            raise ValidationError("The bid must be higher than the minimum bid")
        return self.bid_amount
'''

