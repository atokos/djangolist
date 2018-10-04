from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import AuctionListView, AuctionDetailView, AuctionCreateView

app_name = 'auctions'

urlpatterns = [
    path('', AuctionListView.as_view(), name='list'),
    path('create/', login_required(AuctionCreateView.as_view()), name='create'),
    path('<int:auction_id>/', AuctionDetailView.as_view(), name='detail'),
]
