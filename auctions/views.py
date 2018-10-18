from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views import View
from django.contrib import messages
from django.http import HttpResponseNotFound

from .models import Auction
from .forms import AuctionCreateForm, AuctionEditForm, AuctionBidForm


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
    template_name = 'auctions/auction_create.html'

    def post(self, request):
        form = AuctionCreateForm(request.POST)
        if form.is_valid():
            auction = form.save(commit=False)
            auction.seller = request.user
            auction.save()
            return redirect('auctions:detail', auction_id=auction.id)

        return render(request, self.template_name, {'form': form})

    def get(self, request):
        form = AuctionCreateForm()
        return render(request, self.template_name, {'form': form})


class AuctionDetailView(View):
    template_name = 'auctions/auction_details.html'

    def get(self, request, auction_id):
        auction = Auction.objects.get_by_id(auction_id)
        if auction.is_active():
            context = {'auction': auction}
            return render(request, self.template_name, context)
        else:
            return HttpResponseNotFound


class AuctionEditView(View):
    template_name = 'auctions/auction_edit.html'

    def get(self, request, auction_id):
        auction = get_object_or_404(Auction, id=auction_id)

        if not auction.seller == request.user:
            messages.add_message(request, messages.INFO, "You are not allowed to edit this auction.")
            return redirect(reverse('homepage'))
        else:
            form = AuctionEditForm(instance=auction)
            context = {'form': form,
                       'auction': auction}
            return render(request, self.template_name, context)

    def post(self, request, auction_id):
        auction = get_object_or_404(Auction, pk=auction_id)
        if not auction.seller == request.user:
            messages.add_message(request, messages.INFO, "You are not allowed to edit this auction.")
            return redirect(reverse('homepage'))
        else:
            form = AuctionEditForm(request.POST, instance=auction)
            if form.is_valid():
                auction = form.save()
                return redirect('auctions:detail', auction_id=auction.id)
            else:
                return redirect('homepage')
