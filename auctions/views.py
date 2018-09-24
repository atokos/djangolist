from django.shortcuts import render
from django.http import HttpResponse
from auctions.models import Auction

# Create your views here.
def list(request):
    auctions_list = Auction.objects.all()
    context = {'auctions_list': auctions_list}
    return render(request, 'auctions/list.html', context)

def detail(request):
    HttpResponse("details")