from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views import View
from decimal import *

from .models import Auction
from .forms import AuctionSearchForm, AuctionCreateForm, BidOnAuctionForm


class AuctionListView(View):
    form_class = AuctionSearchForm
    template_name = 'auctions/auction_list.html'

    search_form = AuctionSearchForm()
    create_form = AuctionCreateForm()
    auctions = Auction.objects.filter(state='ACTIVE').order_by('deadline')

    context = {'auctions': auctions,
               'search_form': search_form,
               'create_form': create_form,
               }

    def get(self, request):
        if 'title' in request.GET:
            title = request.GET['title']
            results = get_list_or_404(Auction, title__icontains=title, state='ACTIVE')
            self.context['auctions'] = results
            self.context['title'] = title
        return render(request, self.template_name, self.context)

    def post(self, request):
        form = AuctionCreateForm(request.POST)
        if form.is_valid():
            auction = form.save(commit=False)
            auction.user = request.user
            auction.save()
            return redirect('auctions:list')
        return render(request, self.template_name, self.context)


def auction_detail(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    if (request.method == 'POST') and (request.user != auction.user) and (request.user != auction.latest_bidder):
        form = BidOnAuctionForm(request.POST)
        if form.is_valid():
            bid_amount = form.cleaned_data['amount']    # Retrieve form data
            if bid_amount >= auction.price + Decimal(0.01):      # Validate
                # TODO fix 0.01 problem
                auction.price = bid_amount              # Update the price of auction
                auction.check_deadline(timezone.now())      # Check if the soft deadline is met
                # Register the new latest bidder in the auction model
                latest_bidder = auction.set_latest_bidder(request.user)
                auction.save()                              # Save everything
                # TODO Send mail to seller and old latest bidder
                return redirect('auctions:list')
            else:
                form = BidOnAuctionForm()
    else:
        form = BidOnAuctionForm()
    context = {'auction': auction,
               'form': form}
    return render(request, 'auctions/auction_details.html', context)



