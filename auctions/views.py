from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib import messages
from django.http import HttpResponseNotFound
from decimal import Decimal
from django.utils.translation import gettext as _

from .models import Auction, Bid
from .forms import AuctionCreateForm, AuctionsConfirmCreationForm, AuctionEditForm, AuctionBidForm


class AuctionListView(View):

    def get(self, request):
        auctions = Auction.objects.get_all_active()
        if 'title' in request.GET:
            title = request.GET['title']
            results = Auction.objects.get_by_title(title=title)
            context = {
                'auctions': results,
                'title': title
            }
        else:
            context = {'auctions': auctions}
        return render(request, 'auctions/auction_list.html', context)


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
            messages.success(request, _("New auction has been created"))
            auction.mail_seller("New Auction created", "A new auction was successfully created.")
            return redirect(auction)
        else:
            messages.info(request, _("Auction creation cancelled"))
            return redirect(reverse('auctions:list'))


class AuctionDetailView(View):

    def get(self, request, auction_id):
        auction = Auction.objects.get_by_id(auction_id)
        if auction.is_active():
            context = {'auction': auction}
            return render(request, 'auctions/auction_details.html', context)
        else:
            messages.error(request, _("Requested auction not found!"))
            return redirect(reverse('auctions:list'))

    def post(self, request, auction_id):
        auction = Auction.objects.get_by_id(auction_id)
        if auction.is_active():
            context = {'auction': auction}
            return render(request, 'auctions/auction_bid.html', context)
        else:
            messages.error(request, _("Requested auction not found!"))
            return redirect(reverse('auctions:list'))


class AuctionBidView(View):

    def get(self, request, auction_id):
        auction = Auction.objects.get_by_id(auction_id)
        if auction.is_active():
            if request.user == auction.seller:
                messages.error(request, _("Cannot bid on own auctions!"))
                return redirect(auction)
            if request.user == auction.get_latest_bidder():
                messages.error(request, _("Cannot bid on winning auction!"))
                return redirect(auction)
            form = AuctionBidForm()
            context = {
                'auction': auction,
                'form': form,
            }
            return render(request, 'auctions/auction_bid.html', context)
        else:
            messages.error(request, _("Requested auction not found!"))
            return redirect(reverse('auctions:list'))

    def post(self, request, auction_id):
        auction = Auction.objects.get_by_id(auction_id)
        if auction.is_active():
            if request.user == auction.seller:
                messages.error(request, _("Cannot bid on own auctions!"))
                return redirect(auction)
            if request.user == auction.get_latest_bidder():
                messages.error(request, _("Cannot bid on winning auction!"))
                return redirect(auction)
            if auction.is_active():
                form = AuctionBidForm(request.POST)
                if form.is_valid():
                    bid_amount = form.cleaned_data.get('bid_amount')
                    if bid_amount <= auction.get_latest_bid_amount() + Decimal('0.005'):
                        messages.error(request, _("The bid must be at least 0.01 higher than the current bid"))
                        return redirect(reverse('auctions:bid', args=[str(auction_id)]))
                    if bid_amount < auction.minimum_bid:
                        messages.error(request, _("The bid must be higher than the minimum bid"))
                        return redirect(reverse('auctions:bid', args=[str(auction_id)]))
                    # Mail seller and latest bidder
                    auction.mail_seller("New Bid", "A new bid has been placed on your auction.")
                    auction.mail_latest_bidder("New Bid", "A new bid has been placed on an auction you have bid on.")
                    # Create and save new Bid
                    new_bid = Bid()
                    new_bid.bid_amount = bid_amount
                    new_bid.auction = auction
                    new_bid.bidder = request.user
                    new_bid.save()
                    # Extend deadline if the bid is placed 5 minutes within the deadline
                    auction.check_soft_deadline()
                    messages.success(request, _("The bid was created."))
                    return redirect(auction)
                else:
                    messages.error(request, _("Invalid bid."))
                    return redirect(auction)
        else:
            messages.error(request, _("Requested auction not found!"))
            return redirect(reverse('auctions:list'))


class AuctionEditView(View):
    template_name = 'auctions/auction_edit.html'

    def get(self, request, auction_id):
        auction = Auction.objects.get_by_id(auction_id)
        if auction.is_active():
            if not auction.seller == request.user:
                messages.info(request, _("You are not allowed to edit this auction."))
                return redirect(auction)
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
                messages.info(request, _("You are not allowed to edit this auction."))
                return redirect(auction)
            else:
                form = AuctionEditForm(request.POST, instance=auction)
                if form.is_valid():
                    auction = form.save()
                    return redirect(auction)
                context = {'form': form,
                           'auction': auction}
                return render(request, self.template_name, context)
        else:
            return HttpResponseNotFound


class AuctionBanView(View):

    def get(self, request, auction_id):
        if request.user.has_perm("auctions.ban_auction"):
            auction = Auction.objects.get_by_id(auction_id)
            if auction.is_active():
                auction.ban()
                auction.mail_seller("Auction banned", "Your auction has been banned for breaking the rules.")
                auction.mail_bidders("Auction banned", "The auction you have bid on has been banned.")
                return render(request, 'auctions/auction_ban.html', {'auction': auction})
            else:
                messages.error(request, _("Auction is already banned"))
                return redirect(reverse('auctions:list'))
        else:
            messages.error(request, _("Permission denied"))
            return redirect(reverse('auctions:list'))


class AuctionBannedListView(View):

    def get(self, request):
        if request.user.has_perm("auctions.view_banned_auctions"):
            auctions = Auction.objects.get_all_banned()
            return render(request, 'auctions/auction_banned_list.html', {'banned_auctions': auctions})
        else:
            messages.error(request, _("Permission denied"))
            return redirect(reverse('auctions:list'))
