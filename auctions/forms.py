from django import forms

class AuctionSearchForm(forms.Form):
    q = forms.CharField(label="Title", max_length=100)