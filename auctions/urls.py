from django.urls import path
from . import views

urlpatterns = [
    path('', views.auction_list, name='list'),
    path('<int:auction_id>/', views.auction_detail, name='detail'),
    path('search/', views.search_page, name='search_page'),
    path('search/result/', views.search_result, name='search_result'),
]
