from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views
from .views import AccountChangeEmailView, AccountProfileView, AccountChangePasswordView

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', login_required(AccountProfileView.as_view()), name='profile'),
    path('change-email/', login_required(AccountChangeEmailView.as_view()), name='change-email'),
    path('change-password/', login_required(AccountChangePasswordView.as_view()), name='change-password'),
    path('signup/', views.signup_view, name='signup'),
]
