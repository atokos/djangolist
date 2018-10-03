from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Auction
from .forms import AuctionSearchForm, CreateAuctionForm, BidOnAuctionForm


def auction_list(request):
    auctions = Auction.objects.filter(state='ACTIVE').order_by('deadline')
    context = {'auctions': auctions}
    return render(request, 'auctions/auction_list.html', context)


def auction_detail(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    if (request.method == 'POST') and (request.user != auction.user) and (request.user != auction.latest_bidder):
        form = BidOnAuctionForm(request.POST)
        if form.is_valid():
            bid_amount = form.cleaned_data['amount']    # Retrieve form data
            if bid_amount >= auction.price + 0.01:      # Validate
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


@login_required()
def auction_create(request):
    if request.method == 'POST':
        form = CreateAuctionForm(request.POST)
        if form.is_valid():
            auction = form.save(commit=False)
            auction.user = request.user
            auction.save()
            return redirect('auctions:list')
    else:
        form = CreateAuctionForm()
    context = {'form': form}
    return render(request, 'auctions/auction_create.html', context)


@login_required()
def auction_bid(request, amount):
    pass


def search_page(request):
    form = AuctionSearchForm()
    return render(request, 'auctions/search_page.html', {'form': form})


def search_result(request):
    query = request.GET.__getitem__('q')
    results = get_list_or_404(Auction, title__icontains=query, state='ACTIVE')
    context = {'results': results,
               'query': query}
    return render(request, 'auctions/search_results.html', context)



