from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase, Client
from django.utils import timezone
from decimal import Decimal

from auctions.models import Auction, Bid


class CreateAuctionTest(TestCase):
    fixtures = ['auctions', 'users']

    def test_valid_create(self):
        title = "Test title"
        description = "A test auction."
        minimum_bid = 1
        deadline = timezone.now() + timezone.timedelta(hours=73)
        deadline = deadline.strftime("%Y-%m-%d %H:%M:%S")

        self.client.login(username="testuser0", password="0")

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
        title = "Test title"
        description = "A test auction."
        minimum_bid = 1
        deadline = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        self.client.login(username="testuser0", password="0")

        response = self.client.post(reverse("auctions:create"), {"title": title,
                                                                 "description": description,
                                                                 "minimum_bid": minimum_bid,
                                                                 "deadline": deadline})

        response = self.client.get(reverse("auctions:list"), {'title': "Test title"})
        self.assertEqual(response.status_code, 404)


class BidOnAuctionTest(TestCase):
    fixtures = ['auctions', 'users']

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testuser')

    def test_valid_bid(self):
        self.client.login(username="testuser", password="testuser")
        auction = Auction.objects.get_by_id(2)
        response = self.client.get(reverse("auctions:bid", args=(auction.id, )))
        self.assertEqual(response.status_code, 200)

        bid_count = Bid.objects.count()
        response = self.client.post(reverse("auctions:bid", args=(auction.id, )),
                         {"bid_amount": 50.01, "version": response.context['auction'].version})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(bid_count + 1, Bid.objects.count())

        latest_bid = Auction.objects.get_by_id(2).get_latest_bid()
        self.assertEqual(latest_bid.bid_amount, Decimal("50.01"))
        self.assertEqual(latest_bid.auction, auction)
        self.assertEqual(latest_bid.bidder, self.user)

    def test_bid_too_low(self):
        self.client.login(username="testuser0", password="0")

        auction = Auction.objects.get_by_id(2)

        bid_count = Bid.objects.count()
        response = self.client.post(reverse("auctions:bid", args=(auction.id, )),
                         {"bid_amount": 50, "version": auction.version})
        self.assertEqual(bid_count, Bid.objects.count())

    def test_bid_on_winning_auction(self):
        self.client.login(username="testuser0", password="0")

        auction = Auction.objects.get_by_id(2)

        bid_count = Bid.objects.count()
        response = self.client.post(reverse("auctions:bid", args=(auction.id,)),
                         {"bid_amount": 51, "version": auction.version})
        self.assertEqual(bid_count + 1, Bid.objects.count())

        bid_count = Bid.objects.count()
        response = self.client.post(reverse("auctions:bid", args=(auction.id,)),
                         {"bid_amount": 52, "version": auction.version})
        self.assertEqual(bid_count, Bid.objects.count())

    def test_bid_on_own_auction(self):
        self.client.login(username="testuser0", password="0")

        auction = Auction.objects.get_by_id(1)

        bid_count = Bid.objects.count()
        response = self.client.post(reverse("auctions:bid", args=(auction.id,)),
                         {"bid_amount": 207, "version": auction.version})
        self.assertEqual(bid_count, Bid.objects.count())


    def test_bid_on_banned(self):
        self.client.login(username="testuser0", password="0")

        auction = Auction.objects.get_by_id(2)

        # Bidder gets auction
        response = self.client.get(reverse("auctions:bid", args=(auction.id,)))
        self.assertEqual(response.status_code, 200)

        # Auction gets banned
        auction.banned = True
        auction.save()
        self.assertTrue(auction.banned)

        # Bidder tries to bid
        bid_count = Bid.objects.count()
        response = self.client.post(reverse("auctions:bid", args=(auction.id,)),
                         {"bid_amount": 51, "version": auction.version})
        self.assertEqual(bid_count, Bid.objects.count())

    def test_bid_on_due(self):
        self.client.login(username="testuser0", password="0")

        auction = Auction.objects.get_by_id(2)

        # Bidder gets auction
        response = self.client.get(reverse("auctions:bid", args=(auction.id,)))
        self.assertEqual(response.status_code, 200)

        # Auction gets due
        auction.due = True
        auction.save()
        self.assertTrue(auction.due)

        # Bidder tries to bid
        bid_count = Bid.objects.count()
        response = self.client.post(reverse("auctions:bid", args=(auction.id,)),
                         {"bid_amount": 51, "version": auction.version})
        self.assertEqual(bid_count, Bid.objects.count())

    def test_bid_on_edited_auction(self):
        bidder = Client()
        seller = Client()
        bidder.login(username="testuser0", password="0")
        seller.login(username="testuser1", password="1")

        auction = Auction.objects.get_by_id(2)

        # Bidder gets auction
        bidder_response = bidder.get(reverse("auctions:bid", args=(auction.id,)))
        self.assertEqual(bidder_response.status_code, 200)

        # Seller edits description of auction
        seller_response = seller.post(reverse("auctions:edit", args=(auction.id,)),
                                      {"description": "new description"})
        self.assertEqual(seller_response.status_code, 302)
        updated_auction = Auction.objects.get_by_id(2)
        self.assertEqual(updated_auction.description, "new description")

        # Bidder tries to bid
        bid_count = Bid.objects.count()
        response = self.client.post(reverse("auctions:bid", args=(auction.id,)),
                                    {"bid_amount": 51, "version": bidder_response.context['auction'].version})
        self.assertEqual(bid_count, Bid.objects.count())

    def test_concurrent_bidding(self):
        client1 = Client()
        client2 = Client()
        client1.login(username="testuser6", password="6")
        client2.login(username="testuser7", password="7")

        # Client 1 gets auction
        response1 = client1.get(reverse("auctions:bid", args=(2, )))
        self.assertEqual(response1.status_code, 200)

        # Client 2 gets auction
        response2 = client2.get(reverse("auctions:bid", args=(2, )))
        self.assertEqual(response1.status_code, 200)

        # Client 2 bids on auction
        bid_count = Bid.objects.count()
        response2 = client2.post(reverse("auctions:bid", args=(2, )),
                                    {"bid_amount": 55, "version": response2.context['auction'].version})
        self.assertEqual(bid_count + 1, Bid.objects.count())

        # Client 1 tries to bid on auction after Client 2
        bid_count = Bid.objects.count()
        response = self.client.post(reverse("auctions:bid", args=(2,)),
                                    {"bid_amount": 55, "version": response1.context['auction'].version},)
        auction = Auction.objects.get_by_id(2)
        self.assertEqual(auction.get_latest_bid_amount(), Decimal('55.00'))
        self.assertEqual(bid_count, Bid.objects.count())

    def test_soft_deadline(self):
        self.client.login(username="testuser6", password="6")

        auction = Auction.objects.get_by_id(2)
        auction.deadline = timezone.now() + timezone.timedelta(minutes=5)
        auction.save()
        extended_deadline = auction.deadline + timezone.timedelta(minutes=5)

        bid_count = Bid.objects.count()
        response = self.client.post(reverse("auctions:bid", args=(2,)),
                         {"bid_amount": 51, "version": auction.version})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(bid_count + 1, Bid.objects.count())

        auction = Auction.objects.get_by_id(2)
        self.assertEqual(extended_deadline, auction.deadline)
