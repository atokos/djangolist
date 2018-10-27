from rest_framework import serializers

from .models import Auction


class AuctionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ('id', 'title', 'seller', 'deadline')


class AuctionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ('id', 'title', 'description', 'seller', 'deadline', 'minimum_bid')