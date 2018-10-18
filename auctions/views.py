from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views import View
from django.contrib import messages
from django.http import HttpResponseNotFound

from .models import Auction
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
