from django.urls import path
from . import views

app_name = "auctions"

urlpatterns = [
    path('', views.list_view, name = 'list'),
    path('<int:auction_id>/', views.details_view, name = 'detail'),
]