from django import forms
from .models import Auction, Bid
from django.utils import timezone


class AuctionCreateForm(forms.ModelForm):

    class Meta:
        model = Auction
        fields = ['title', 'description', 'minimum_bid', 'deadline']

    def clean_minimum_bid(self):
        minimum_bid = self.cleaned_data.get('minimum_bid')
        if not minimum_bid > 0:
            raise forms.ValidationError("The price must be a positive number greater than zero.")
        return minimum_bid

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if not deadline > (timezone.now() + timezone.timedelta(hours=72)):
            raise forms.ValidationError("This deadline is too soon, the minimum is 72h from now.")
        return deadline


class AuctionsConfirmCreationForm(forms.Form):
    CHOICES = [(x, x) for x in ("Yes", "No")]
    option = forms.ChoiceField(choices=CHOICES)
    title = forms.CharField(widget=forms.HiddenInput())
    description = forms.CharField(widget=forms.HiddenInput())
    minimum_bid = forms.DecimalField(widget=forms.HiddenInput())
    deadline = forms.DateTimeField(widget=forms.HiddenInput())


class AuctionEditForm(forms.ModelForm):

    class Meta:
        model = Auction
        fields = ['description']


class AuctionBidForm(forms.ModelForm):

    class Meta:
        model = Bid
        fields = ['bid_amount']





