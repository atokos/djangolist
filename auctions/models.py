from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.core.mail import send_mail


class AuctionManager(models.Manager):

    def get_all_active(self):
        return self.filter(banned=False, due=False)

    def get_all_banned(self):
        return self.filter(banned=True)

    def get_all_due(self):
        active_auctions = self.filter(banned=False)
        due_auctions = []
        for auction in active_auctions:
            if auction.deadline < timezone.now():
                auction.set_due()
                due_auctions.append(auction)
        return due_auctions

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
    version = models.IntegerField(default=1)

    banned = models.BooleanField(default=False)
    due = models.BooleanField(default=False)

    objects = AuctionManager()

    class Meta:
        permissions = (
            ("ban_auction", "Can ban an auction"),
            ("view_banned_auctions", "Can view banned auctions"),
        )

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
            return 0
        return self.get_latest_bid().bid_amount

    def get_losers(self):
        if not self.bid_set.all():
            return None
        losers = []
        winner = self.get_latest_bidder()
        bidders = self.bid_set.all()
        for bidder in bidders:
            if bidder is not winner:
                losers.append(bidder)
        return losers

    def ban(self):
        self.banned = True
        self.save()

    def set_due(self):
        self.due = True
        self.save()

    def check_soft_deadline(self):
        if timezone.now() >= self.deadline - timezone.timedelta(minutes=5):
            self.deadline += timezone.timedelta(minutes=5)
            self.save()


class Bid(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    auction = models.ForeignKey(Auction, default=None, on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    bid_amount = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.bidder.username + ': ' + str(self.bid_amount)


class Currency(models.Model):
    code = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=8, decimal_places=6)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def needs_update(self):
        if timezone.now() - self.updated < timezone.timedelta(seconds=15):
            return True
        else:
            return False



