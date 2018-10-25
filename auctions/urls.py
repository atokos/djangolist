from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import (
    AuctionListView,
    AuctionDetailView,
    AuctionCreateView,
    AuctionEditView,
    AuctionConfirmCreationView,
    AuctionBidView,
    AuctionBanView,
    AuctionBannedListView,
    fetch_exchange_rate,
)

app_name = 'auctions'

urlpatterns = [
    path('', AuctionListView.as_view(), name='list'),
    path('currency/', fetch_exchange_rate, name='currency'),
    path('banned/', AuctionBannedListView.as_view(), name='banned-list'),
    path('create/', login_required(AuctionCreateView.as_view()), name='create'),
    path('confirm/', login_required(AuctionConfirmCreationView.as_view()), name='confirm'),
    path('<int:auction_id>/', AuctionDetailView.as_view(), name='detail'),
    path('<int:auction_id>/edit/', login_required(AuctionEditView.as_view()), name='edit'),
    path('<int:auction_id>/ban/', AuctionBanView.as_view(), name='ban'),
    path('<int:auction_id>/bid/', login_required(AuctionBidView.as_view()), name='bid'),
]
