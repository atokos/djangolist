from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views
from .views import AccountChangeEmailView, AccountProfileView, AccountChangePasswordView, AccountSetPreferencesView

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('preference/', login_required(AccountSetPreferencesView.as_view()), name='set-preferences'),
    path('profile/', login_required(AccountProfileView.as_view()), name='profile'),
    path('change-email/', login_required(AccountChangeEmailView.as_view()), name='change-email'),
    path('change-password/', login_required(AccountChangePasswordView.as_view()), name='change-password'),
    path('signup/', views.signup_view, name='signup'),
]
