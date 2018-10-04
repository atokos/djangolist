from django.urls import path

from .views import AuctionListView
from . import views

app_name = 'auctions'

urlpatterns = [
    path('', AuctionListView.as_view(), name='list'),
    path('<int:auction_id>/', views.auction_detail, name='detail'),
]
