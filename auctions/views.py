from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib import messages
from django.http import HttpResponseNotFound
from decimal import Decimal

from .models import Auction, Bid
from .forms import AuctionCreateForm, AuctionsConfirmCreationForm, AuctionEditForm, AuctionBidForm


class AuctionListView(View):
    template_name = 'auctions/auction_list.html'
    auctions = Auction.objects.get_all_active()
    context = {
        'auctions': auctions
    }

    def get(self, request):
        if 'title' in request.GET:
            title = request.GET['title']
            results = Auction.objects.get_by_title(title=title)
            self.context['auctions'] = results
            self.context['title'] = title
        return render(request, self.template_name, self.context)


class AuctionCreateView(View):

    def post(self, request):
        form = AuctionCreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            minimum_bid = form.cleaned_data['minimum_bid']
            deadline = form.cleaned_data['deadline']

            initial_data = {
                'title': title,
                'description': description,
                'minimum_bid': minimum_bid,
                'deadline': deadline,
            }
            form = AuctionsConfirmCreationForm(initial=initial_data)
            return render(request, 'auctions/auction_confirm.html', {'form': form})
        return render(request, 'auctions/auction_create.html', {'form': form})

    def get(self, request):
        form = AuctionCreateForm()
        return render(request, 'auctions/auction_create.html', {'form': form})


class AuctionConfirmCreationView(View):

    def post(self, request):
        option = request.POST.get('option', '')
        if option == 'Yes':
            title = request.POST.get('title')
            description = request.POST.get('description', '')
            minimum_bid = request.POST.get('minimum_bid', '')
            deadline = request.POST.get('deadline', '')
            seller = request.user
            auction = Auction(
                title=title,
                description=description,
                minimum_bid=minimum_bid,
                deadline=deadline,
                seller=seller
            )
            auction.save()
            messages.add_message(request, messages.INFO, "New auction has been created")
            return redirect(auction)
        else:
            messages.add_message(request, messages.INFO, "Auction creation cancelled")
            return redirect(reverse('auctions:list'))


class AuctionDetailView(View):

    def get(self, request, auction_id):
        auction = Auction.objects.get_by_id(auction_id)
        if auction.is_active():
            context = {'auction': auction}
            return render(request, 'auctions/auction_details.html', context)
        else:
            return HttpResponseNotFound

    def post(self, request, auction_id):
        auction = Auction.objects.get_by_id(auction_id)
        if auction.is_active():
            context = {'auction': auction}
            return render(request, 'auctions/auction_bid.html', context)
        else:
            return HttpResponseNotFound


class AuctionBidView(View):

    def get(self, request, auction_id):
        auction = Auction.objects.get_by_id(auction_id)
        if auction.is_active():
            if request.user == auction.seller:
                messages.add_message(request, messages.ERROR, "Cannot bid on own auctions!")
                return redirect(auction)
            if request.user == auction.get_latest_bidder():
                messages.add_message(request, messages.ERROR, "Cannot bid on winning auction!")
                return redirect(auction)
            form = AuctionBidForm()
            context = {
                'auction': auction,
                'form': form,
            }
            return render(request, 'auctions/auction_bid.html', context)
        else:
            return HttpResponseNotFound

    def post(self, request, auction_id):
        auction = Auction.objects.get_by_id(auction_id)
        if auction.is_active():
            if request.user == auction.seller:
                messages.add_message(request, messages.ERROR, "Cannot bid on own auctions!")
                return redirect(auction)
            if request.user == auction.get_latest_bidder():
                messages.add_message(request, messages.ERROR, "Cannot bid on winning auction!")
                return redirect(auction)
            if auction.is_active():
                form = AuctionBidForm(request.POST)
                if form.is_valid():
                    bid_amount = form.cleaned_data.get('bid_amount')
                    if bid_amount < auction.get_latest_bid_amount() + Decimal('0.01'):
                        messages.add_message(
                            request,
                            messages.ERROR,
                            "The bid must be at least 0.01 higher than the current bid"
                        )
                        return redirect(reverse('auctions:bid', args=[str(auction_id)]))
                    if bid_amount < auction.minimum_bid:
                        messages.add_message(
                            request,
                            messages.ERROR,
                            "The bid must be higher than the minimum bid"
                        )
                        return redirect(reverse('auctions:bid', args=[str(auction_id)]))
                    new_bid = Bid()
                    new_bid.bid_amount = bid_amount
                    new_bid.auction = auction
                    new_bid.bidder = request.user
                    new_bid.save()
                    #TODO Send mail to latest bidder and the seller
                    #TODO Soft deadlines
                    return redirect(auction)
                else:
                    messages.add_message(request, messages.ERROR, "Invalid bid.")
                    return redirect(auction)
        else:
            return HttpResponseNotFound


class AuctionEditView(View):
    template_name = 'auctions/auction_edit.html'

    def get(self, request, auction_id):
        auction = Auction.objects.get_by_id(auction_id)
        if auction.is_active():
            if not auction.seller == request.user:
                messages.add_message(request, messages.INFO, "You are not allowed to edit this auction.")
                return redirect(reverse('auctions:list'))
            else:
                form = AuctionEditForm(instance=auction)
                context = {'form': form,
                           'auction': auction}
                return render(request, self.template_name, context)
        else:
            return HttpResponseNotFound

    def post(self, request, auction_id):
        auction = Auction.objects.get_by_id(auction_id)
        if auction.is_active():
            if not auction.seller == request.user:
                messages.add_message(request, messages.INFO, "You are not allowed to edit this auction.")
                return redirect(reverse('auctions:list'))
            else:
                form = AuctionEditForm(request.POST, instance=auction)
                if form.is_valid():
                    auction = form.save()
                    return redirect('auctions:detail', auction_id=auction.id)
                else:
                    return redirect('auctions:list')
        else:
            return HttpResponseNotFound
