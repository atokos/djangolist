from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase, Client
from django.utils import timezone
from decimal import Decimal

from auctions.models import Auction, Bid


class CreateAuctionTest(TestCase):
    fixtures = ['auction']

    def test_valid_create(self):
        self.user = User.objects.create_user(username="testuser", password="1234")
        title = "Test title"
        description = "A test auction."
        minimum_bid = 1
        deadline = timezone.now() + timezone.timedelta(hours=73)
        deadline = deadline.strftime("%Y-%m-%d %H:%M:%S")

        self.client.login(username="testuser", password="1234")

        response = self.client.post(reverse("auctions:create"), {"title": title,
                                                                 "description": description,
                                                                 "minimum_bid": minimum_bid,
                                                                 "deadline": deadline})

        self.assertTemplateUsed(response, "auctions/auction_confirm.html")

        response = self.client.post(reverse("auctions:confirm"), {"option": "Yes",
                                                                  "title": title,
                                                                  "description": description,
                                                                  "minimum_bid": minimum_bid,
                                                                  "deadline": deadline})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse("auctions:list"), {'title': "Test title"})
        self.assertEqual(response.status_code, 200)

    def test_invalid_time(self):
        self.user = User.objects.create_user(username="testuser", password="1234")
        title = "Test title"
        description = "A test auction."
        minimum_bid = 1
        deadline = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        self.client.login(username="testuser", password="1234")

        response = self.client.post(reverse("auctions:create"), {"title": title,
                                                                 "description": description,
                                                                 "minimum_bid": minimum_bid,
                                                                 "deadline": deadline})

        response = self.client.get(reverse("auctions:list"), {'title': "Test title"})
        self.assertEqual(response.status_code, 404)


class BidOnAuctionTest(TestCase):

    def setUp(self):
        self.seller = User.objects.create(username='seller', password='1234')
        self.user1 = User.objects.create_user(username="testuser1", password="1234")
        self.user2 = User.objects.create_user(username="testuser2", password="1234")
        self.superuser = User.objects.create_superuser(username="admin", password="1234", email="test@example.com")
        deadline = timezone.now() + timezone.timedelta(minutes=4)
        # deadline = deadline.strftime("%Y-%m-%d %H:%M:%S")
        self.auction = Auction.objects.create(
            seller=self.seller,
            title="Test",
            description="Description",
            minimum_bid="10",
            deadline=deadline
        )


    def tearDown(self):
        del self.auction
        del self.seller
        del self.user1
        del self.user2
        del self.superuser

    def test_valid_bid(self):
        self.client.login(username="testuser1", password="1234")

        response = self.client.get(reverse("auctions:bid", args=(self.auction.id, )))
        self.assertEqual(response.status_code, 200)

        bid_count = Bid.objects.count()
        response = self.client.post(reverse("auctions:bid", args=(self.auction.id, )),
                         {"bid_amount": 10.01, "version": response.context['auction'].version})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(bid_count + 1, Bid.objects.count())

        latest_bid = Auction.objects.get_by_id(1).get_latest_bid()
        self.assertEqual(latest_bid.bid_amount, Decimal("10.01"))
        self.assertEqual(latest_bid.auction, self.auction)
        self.assertEqual(latest_bid.bidder, self.user1)

    def test_bid_too_low(self):
        self.client.login(username="testuser1", password="1234")

        bid_count = Bid.objects.count()
        response = self.client.post(reverse("auctions:bid", args=(self.auction.id, )),
                         {"bid_amount": 10, "version": self.auction.version})
        self.assertEqual(bid_count, Bid.objects.count())

    def test_bid_on_own_auction(self):
        self.client.login(username="testuser1", password="1234")

        bid_count = Bid.objects.count()
        response = self.client.post(reverse("auctions:bid", args=(self.auction.id,)),
                         {"bid_amount": 15, "version": self.auction.version})
        self.assertEqual(bid_count + 1, Bid.objects.count())

        bid_count = Bid.objects.count()
        response = self.client.post(reverse("auctions:bid", args=(self.auction.id,)),
                         {"bid_amount": 20, "version": self.auction.version})
        self.assertEqual(bid_count, Bid.objects.count())

    def test_bid_on_winning_auction(self):
        self.client.login(username="seller", password="1234")

        bid_count = Bid.objects.count()
        response = self.client.post(reverse("auctions:bid", args=(self.auction.id,)),
                         {"bid_amount": 15, "version": self.auction.version})
        self.assertEqual(bid_count, Bid.objects.count())

    def test_bid_on_banned(self):
        bidder = Client()
        admin = Client()
        bidder.login(username="testuser1", password="1234")
        admin.login(username="admin", password="1234")

        # Bidder gets auction
        response = bidder.get(reverse("auctions:bid", args=(self.auction.id,)))
        self.assertEqual(response.status_code, 200)

        # Admin bans auction
        admin.post(reverse("auctions:ban", args=(self.auction.id,)))
        self.auction.banned = True
        self.auction.save()
        self.assertTrue(self.auction.banned)

        # Bidder tries to bid
        bid_count = Bid.objects.count()
        response = bidder.post(reverse("auctions:bid", args=(self.auction.id,)),
                         {"bid_amount": 20, "version": self.auction.version})
        self.assertEqual(bid_count, Bid.objects.count())

    def test_bid_on_edited_auction(self):
        bidder = Client()
        seller = Client()
        bidder.login(username="testuser1", password="1234")
        seller.login(username="seller", password="1234")

        # Bidder gets auction
        bidder_response = bidder.get(reverse("auctions:bid", args=(self.auction.id,)))
        self.assertEqual(bidder_response.status_code, 200)

        # Seller edits description of auction
        seller_response = seller.post(reverse("auctions:edit", args=(self.auction.id,)),
                               {"description": "new description"})
        self.assertTemplateUsed(seller_response, 'auctions/auction_edit.html')
        self.assertEqual(self.auction.description, "new description")

        # Bidder tries to bid
        bid_count = Bid.objects.count()
        response = self.client.post(reverse("auctions:bid", args=(self.auction.id,)),
                                    {"bid_amount": 20, "version": bidder_response.context['auction'].version})
        self.assertEqual(bid_count, Bid.objects.count())

    def test_concurrent_bidding(self):
        client1 = Client()
        client2 = Client()
        client1.login(username="testuser1", password="1234")
        client2.login(username="testuser2", password="1234")

        # Client 1 gets auction
        response1 = client1.get(reverse("auctions:bid", args=(self.auction.id,)))
        self.assertEqual(response1.status_code, 200)

        # Client 2 gets auction
        response2 = client2.get(reverse("auctions:bid", args=(self.auction.id,)))
        self.assertEqual(response1.status_code, 200)

        # Client 2 bids on auction
        bid_count = Bid.objects.count()
        response2 = client2.post(reverse("auctions:bid", args=(self.auction.id,)),
                                    {"bid_amount": 20, "version": response2.context['auction'].version})
        self.assertEqual(bid_count + 1, Bid.objects.count())

        # Client 1 tries to bid on auction after Client 2
        bid_count = Bid.objects.count()
        response = self.client.post(reverse("auctions:bid", args=(self.auction.id,)),
                                    {"bid_amount": 15, "version": response1.context['auction'].version},)
        self.assertEqual(bid_count, Bid.objects.count())

    def test_soft_deadline(self):
        self.client.login(username="testuser1", password="1234")

        extended_deadline = self.auction.deadline + timezone.timedelta(minutes=5)

        bid_count = Bid.objects.count()
        self.client.post(reverse("auctions:bid", args=(self.auction.id,)),
                         {"bid_amount": 15, "version": self.auction.version})
        self.assertEqual(bid_count + 1, Bid.objects.count())

        self.assertEqual(extended_deadline, self.auction.deadline)
