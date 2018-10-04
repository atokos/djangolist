from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views
from .views import AccountEditEmailView

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('edit/', login_required(AccountEditEmailView.as_view()), name='edit'),
    path('signup/', views.signup_view, name='signup'),
]
