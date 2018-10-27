from django.shortcuts import render, redirect, reverse, get_list_or_404
from django.views import View
from django.contrib import messages
from decimal import Decimal
from django.utils.translation import gettext as _

from .models import Auction, Bid, Currency
from .forms import AuctionCreateForm, AuctionsConfirmCreationForm, AuctionEditForm, AuctionBidForm


class AuctionListView(View):

    def get(self, request):
        print("list")
        auctions = Auction.objects.get_all_active()
        if 'title' in request.GET:
            title = request.GET['title']
            results = get_list_or_404(Auction, title=title, banned=False, due=False)
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

            subject = "New Auction %s created!" % title
            body = "The new auction named %s was successfully created." % title
            seller.email_user(subject, body)

            return redirect(auction)
        else:
            messages.info(request, _("Auction creation cancelled"))
            return redirect(reverse('auctions:list'))


class AuctionDetailView(View):

    def get(self, request, auction_id):
        auction = Auction.objects.get_by_id(auction_id)
        if not auction.is_active():
            messages.error(request, _("Requested auction not found!"))
            return redirect(reverse('auctions:list'))
        if 'currency' in request.session:
            currency = request.session['currency']
        else:
            currency = 'EUR'
        if currency == 'EUR':
            context = {
                'auction': auction,
                'latest_bid': auction.get_latest_bid_amount(),
                'currency': currency
            }
        else:
            rate = Currency.objects.get(code=currency).rate
            converted_min_bid = convert(auction.minimum_bid, rate)
            context = {
                'auction': auction,
                'converted_min_bid': converted_min_bid,
                'latest_bid': convert(auction.get_latest_bid_amount(), rate),
                'currency': currency
            }
        return render(request, 'auctions/auction_details.html', context)


class AuctionBidView(View):

    def get(self, request, auction_id):
        auction = Auction.objects.get_by_id(auction_id)
        if not auction.is_active():
            messages.error(request, _("Requested auction not found!"))
            return redirect(reverse('auctions:list'))
        if request.user == auction.seller:
            messages.error(request, _("Cannot bid on own auctions!"))
            return redirect(auction)
        if request.user == auction.get_latest_bidder():
            messages.error(request, _("Cannot bid on winning auction!"))
            return redirect(auction)
        form = AuctionBidForm()
        if 'currency' in request.session:
            currency = request.session['currency']
        else:
            currency = 'EUR'
        if currency == 'EUR':
            context = {
                'auction': auction,
                'latest_bid': auction.get_latest_bid_amount(),
                'form': form,
                'currency': currency
            }
        else:
            rate = Currency.objects.get(code=currency).rate
            converted_min_bid = convert(auction.minimum_bid, rate)
            context = {
                'auction': auction,
                'converted_min_bid': converted_min_bid,
                'latest_bid': convert(auction.get_latest_bid_amount(), rate),
                'form': form,
                'currency': currency
            }
        return render(request, 'auctions/auction_bid.html', context)

    def post(self, request, auction_id):
        auction = Auction.objects.get_by_id(auction_id)
        if not auction.is_active():
            messages.error(_("The auction you tried to bid on is not available anymore"))
            return redirect(reverse('auctions:list'))
        if request.user == auction.seller:
            messages.error(request, _("Cannot bid on own auctions!"))
            return redirect(auction)
        if request.user == auction.get_latest_bidder():
            messages.error(request, _("Cannot bid on winning auction!"))
            return redirect(auction)
        form = AuctionBidForm(request.POST)
        if form.is_valid():
            version = int(request.POST['version'])
            bid_amount = form.cleaned_data.get('bid_amount')

            if version is not auction.version:
                messages.error(_("The description has been updated before you put the bid, try to bid again"))
                return redirect(reverse(auction))
            if bid_amount < auction.get_latest_bid_amount() + Decimal('0.01'):
                messages.error(request, _("The bid must be at least 0.01 higher than the current bid"))
                return redirect(reverse('auctions:bid', args=[str(auction_id)]))
            if bid_amount < auction.minimum_bid + Decimal('0.01'):
                messages.error(request, _("The bid must be higher than the minimum bid"))
                return redirect(reverse('auctions:bid', args=[str(auction_id)]))

            # Mail seller and latest bidder
            seller = auction.seller
            bids = auction.bid_set.all()
            title = auction.title
            subject = "New Bid on auction %s" % title
            seller_body = "A new bid has been placed on your auction %s." % title
            bidder_body = "A new bid has been placed on the auction %s, that you have bid on." % title
            seller.email_user(subject, seller_body)
            for bid in bids:
                bid.bidder.email_user(subject, bidder_body)

            # Create and save new Bid
            new_bid = Bid()
            new_bid.bid_amount = bid_amount
            new_bid.auction = auction
            new_bid.bidder = request.user
            new_bid.save()

            # Update auction version
            auction.version += 1
            auction.save()

            # Extend deadline if the bid is placed 5 minutes within the deadline
            auction.check_soft_deadline()
            messages.success(request, _("The bid was created."))
            return redirect(auction)
        else:
            messages.error(request, _("Invalid bid."))
            return redirect(auction)


class AuctionEditView(View):
    template_name = 'auctions/auction_edit.html'

    def get(self, request, auction_id):
        auction = Auction.objects.get_by_id(auction_id)
        if not auction.is_active():
            messages.error(_("The auction you tried to edit is not available"))
            return redirect(reverse('auctions:list'))
        if not auction.seller == request.user:
            messages.info(request, _("You are not allowed to edit this auction."))
            return redirect(auction)
        else:
            form = AuctionEditForm(instance=auction)
            context = {'form': form,
                       'auction': auction}
            return render(request, self.template_name, context)

    def post(self, request, auction_id):
        auction = Auction.objects.get_by_id(auction_id)
        if not auction.is_active():
            messages.info(request, _("The auction you tried to edit is not available"))
            return redirect(reverse('auctions:list'))
        if not auction.seller == request.user:
            messages.info(request, _("You are not allowed to edit this auction."))
            return redirect(auction)
        else:
            form = AuctionEditForm(request.POST, instance=auction)
            if form.is_valid():
                auction = form.save(commit=False)
                auction.version += 1
                auction.save()

                return redirect(auction)
            context = {'form': form,
                       'auction': auction}
            return render(request, self.template_name, context)


class AuctionBanView(View):

    def get(self, request, auction_id):
        if not request.user.has_perm("auctions.ban_auction"):
            messages.error(request, _("Permission denied"))
            return redirect(reverse('auctions:list'))
        auction = Auction.objects.get_by_id(auction_id)
        if not auction.is_active():
            messages.error(request, _("Auction is already banned or due"))
            return redirect(reverse('auctions:list'))
        auction.ban()
        # Mail seller and bidders
        seller = auction.seller
        bids = auction.bid_set.all()
        title = auction.title
        subject = "Auction %s banned" % title
        seller_body = "Your auction %s has been banned for breaking the rules." % title
        bidder_body = "The auction %s, that you have bid on has been banned." % title
        seller.email_user(subject, seller_body)
        for bid in bids:
            bid.bidder.email_user(subject, bidder_body)
        return render(request, 'auctions/auction_ban.html', {'auction': auction})


class AuctionBannedListView(View):

    def get(self, request):
        if request.user.has_perm("auctions.view_banned_auctions"):
            auctions = Auction.objects.get_all_banned()
            return render(request, 'auctions/auction_banned_list.html', {'banned_auctions': auctions})
        else:
            messages.error(request, _("Permission denied"))
            return redirect(reverse('auctions:list'))


def convert(amount, rate):
    new_amount = amount * rate
    output = round(new_amount, 2)
    return output

