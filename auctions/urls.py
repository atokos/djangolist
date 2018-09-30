from django.urls import path
from . import views

app_name = 'auctions'

urlpatterns = [
    path('', views.auction_list, name='list'),
    path('create/', views.auction_create, name='create'),
    path('search/', views.search_page, name='search_page'),
    path('search/result/', views.search_result, name='search_result'),
    path('<int:auction_id>/', views.auction_detail, name='detail'),
]
