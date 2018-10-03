from django import forms
from . import models
from datetime import timedelta
from django.utils import timezone


class AuctionSearchForm(forms.Form):
    q = forms.CharField(label="Title", max_length=100)


class CreateAuctionForm(forms.ModelForm):
    deadline = forms.DateTimeField(widget=forms.DateTimeInput)

    class Meta:
        model = models.Auction
        fields = ['title', 'description', 'price', 'deadline']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if not price > 0:
            raise forms.ValidationError("The price must be a positive number that is not 0.")
        return price

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if not deadline > (timezone.now() + timedelta(hours=72)):
            raise forms.ValidationError("This deadline is too soon, the minimum is 72h from now.")
        return deadline


class BidOnAuctionForm(forms.ModelForm):

    class Meta:
        model = models.Bid
        fields = ['amount']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if not amount >= 0.01:
            raise forms.ValidationError("The minimum bid amount is 0.01.")




