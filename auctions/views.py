from django.shortcuts import render, get_object_or_404
from auctions.models import Auction


def auction_list(request):
    auctions = Auction.objects.all().order_by('deadline')
    context = {'auctions': auctions}
    return render(request, 'auctions/auction_list.html', context)


def auction_detail(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    context = {'auction': auction}
    return render(request, 'auctions/auction_details.html', context)


# TODO search method
# TODO bid method
