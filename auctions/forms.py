from django import forms
from django.forms import ValidationError
from . import models
from datetime import timedelta
from django.utils import timezone


class AuctionSearchForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100)


class AuctionCreateForm(forms.ModelForm):

    class Meta:
        model = models.Auction
        fields = ['title', 'description', 'minimum_bid', 'deadline']

    def __init__(self, *args, **kwargs):
        self.seller = kwargs.pop('seller')
        super(AuctionCreateForm, self).__init__(*args, *kwargs)

    def clean_minimum_bid(self):
        minimum_bid = self.cleaned_data.get('minimum_bid')
        if not minimum_bid > 0:
            raise forms.ValidationError("The price must be a positive number greater than zero.")
        return minimum_bid

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if not deadline > (timezone.now() + timedelta(hours=72)):
            raise forms.ValidationError("This deadline is too soon, the minimum is 72h from now.")
        return deadline

    def save(self, commit=True):
        auction = super(AuctionCreateForm, self).save(commit=False)
        auction.seller = self.seller
        if commit:
            auction.save()
        return auction


class AuctionEditForm(forms.ModelForm):
    class Meta:
        model = models.Auction
        fields = ['description']

    def save(self, commit=True):
        auction = super(AuctionEditForm, self).save(commit=False)
        auction.description = self.cleaned_data['description']
        if commit:
            auction.save()
        return auction


class BidOnAuctionForm(forms.Form):
    amount = forms.DecimalField(max_digits=8, decimal_places=2, required=True)





