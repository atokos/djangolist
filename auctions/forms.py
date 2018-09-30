from django import forms
from . import models


class AuctionSearchForm(forms.Form):
    q = forms.CharField(label="Title", max_length=100)


class CreateArticleForm(forms.ModelForm):
    class Meta:
        model = models.Auction
        fields = ['title', 'description', 'price', 'deadline']
