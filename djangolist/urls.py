from django.contrib import admin
from django.urls import include, path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auctions/', include('auctions.urls')),
    path('accounts/', include('accounts.urls')),
    path('', views.homepage, name="homepage"),
]

urlpatterns += staticfiles_urlpatterns()
