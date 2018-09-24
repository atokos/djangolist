from django.urls import path
from . import views

app_name = "auctions"

urlpatterns = [
    path('', views.list, name = 'list'),
    path('<int:auction_id>/', views.detail, name = 'detail'),
]