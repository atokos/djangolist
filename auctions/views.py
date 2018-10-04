from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.views import View
from decimal import *

from .models import Auction
from .forms import AuctionSearchForm, AuctionCreateForm, AuctionEditForm, BidOnAuctionForm


class AuctionListView(View):
    template_name = 'auctions/auction_list.html'

    form = AuctionSearchForm()
    auctions = Auction.objects.filter(state='ACTIVE').order_by('deadline')

    context = {'auctions': auctions,
               'form': form,
               }

    def get(self, request):
        if 'title' in request.GET:
            title = request.GET['title']
            results = get_list_or_404(Auction, title__icontains=title, state='ACTIVE')
            self.context['auctions'] = results
            self.context['title'] = title
        return render(request, self.template_name, self.context)


class AuctionCreateView(View):
    template_name = 'auctions/auction_create.html'
    form = AuctionCreateForm()
    context = {'form': form}

    def post(self, request):
        form = AuctionCreateForm(request.POST)
        if form.is_valid():
            auction = form.save(commit=False)
            auction.user = request.user
            auction.save()
            return redirect('auctions:detail', auction_id=auction.id)
        else:
            return render(request, self.template_name, self.context)

    def get(self, request):
        return render(request, self.template_name, self.context)


class AuctionDetailView(View):
    template_name = 'auctions/auction_details.html'
    form = BidOnAuctionForm()
    context = {'form': form}

    def post(self, request, auction_id):
        auction = get_object_or_404(Auction, pk=auction_id)
        self.context['auction'] = auction
        if request.user == auction.user:
            error = "You cannot bid on your own auction."
            self.context['error'] = error
            return render(request, self.template_name, self.context)
        if request.user == auction.latest_bidder:
            error = "You cannot bid on an auction you are already winning."
            self.context['error'] = error
            return render(request, self.template_name, self.context)
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % ('accounts:login', request.path))
        else:  # User can bid
            form = BidOnAuctionForm(request.POST)
            if form.is_valid():
                bid = form.cleaned_data['amount']
                if not bid >= Decimal(auction.price) + Decimal(0.005):
                    error = "Bid amount has to be at least 0.01€ higher than the price or previous bid"
                    self.context['error'] = error
                    return render(request, self.template_name, self.context)
                else:
                    # TODO fix 0.01 problem
                    auction.price = bid_amount  # Update the price of auction
                    auction.check_deadline(timezone.now())  # Check if the soft deadline is met
                    # Register the new latest bidder in the auction model
                    latest_bidder = auction.set_latest_bidder(request.user)
                    auction.save()  # Save everything
                    # TODO Send mail to seller and old latest bidder
                    return redirect('auctions:detail', auction_id=auction.id)
            else:
                return render(request, self.template_name, self.context)

    def get(self, request, auction_id):
        auction = get_object_or_404(Auction, pk=auction_id, state='ACTIVE')
        self.context = {'form': self.form,
                        'auction': auction}
        return render(request, self.template_name, self.context)


class AuctionEditView(View):
    template_name = 'auctions/auction_edit.html'

    def get(self, request, auction_id):
        auction = get_object_or_404(Auction, pk=auction_id, state='ACTIVE')
        if not auction.user == request.user:
            return HttpResponseForbidden
        else:
            form = AuctionEditForm(instance=auction)
            context = {'form': form,
                       'auction': auction}
            return render(request, self.template_name, context)

    def post(self, request, auction_id):
        auction = get_object_or_404(Auction, pk=auction_id, state='ACTIVE')
        if not auction.user == request.user:
            return HttpResponseForbidden
        else:
            form = AuctionEditForm(request.POST, instance=auction)
            if form.is_valid():
                auction = form.save()
                return redirect('auctions:detail', auction_id=auction.id)
            else:
                return redirect('homepage')
