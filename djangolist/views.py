from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from auctions.models import Auction, Bid
from djangolist import settings

import random
import os


def generate_data(request):

    for number in range(50):
        username = ("testuser%d" % number)
        password = number
        email = ("testuser%d@example.com" % number)
        user = User.objects.create_user(username=username, email=email, password=password)

        if not number == 0:
            bid = auction.bid_set.create(bidder=user, auction=auction, bid_amount=auction.minimum_bid + 10)
            bid.save()

        auction = Auction()
        auction.seller = user
        auction.title = ("Test auction %d" % number)
        auction.description = "Lorem ipsum dolor sit amet"
        auction.minimum_bid = random.randint(10, 200)
        auction.deadline = timezone.now() + timezone.timedelta(hours=72)
        auction.save()

    messages.info(request, "Data generated")
    return redirect(reverse('homepage'))


def email_history_view(request):
    path = settings.EMAIL_FILE_PATH
    data = []
    for filename in os.listdir(path):
        file = open(os.path.join(path, filename), 'r')
        content = file.readlines()
        for line in content:
            if 'Content-Type' in line:
                content.remove(line)
            if 'MIME-Version' in line:
                content.remove(line)
            if 'Message-ID' in line:
                content.remove(line)
            if 'Content-Transfer-Encoding' in line:
                content.remove(line)
        data.append(content)
    return render(request, 'emailhistory.html', {'data': data})
