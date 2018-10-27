from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.shortcuts import get_object_or_404, get_list_or_404

from .models import Auction
from .serializers import AuctionDetailSerializer, AuctionListSerializer

@api_view(['GET'])
@renderer_classes([JSONRenderer])
def auction_list(request):
    if 'title' in request.GET:
        title = request.GET['title']
        auctions = get_list_or_404(Auction, title=title, banned=False, due=False)
    else:
        auctions = get_list_or_404(Auction, banned=False, due=False)
    serializer = AuctionListSerializer(auctions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def auction_detail(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id, banned=False, due=False)
    serializer = AuctionDetailSerializer(auction)
    return Response(serializer.data)