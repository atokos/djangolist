from django.urls import path
from . import views

app_name = "auctions"

urlpatterns = [
    path('', views.auction_list, name='list'),
    path('<int:auction_id>/', views.auction_detail, name='detail'),
]
#TODO url for searching