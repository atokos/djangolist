from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Auction
from .forms import AuctionSearchForm, CreateAuctionForm


def auction_list(request):
    auctions = Auction.objects.filter(state='ACTIVE').order_by('deadline')
    context = {'auctions': auctions}
    return render(request, 'auctions/auction_list.html', context)


def auction_detail(request, pk):
    auction = get_object_or_404(Auction, pk=pk)
    context = {'auction': auction}
    return render(request, 'auctions/auction_details.html', context)


@login_required()
def auction_create(request):
    if request.method == 'POST':
        form = CreateAuctionForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
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



