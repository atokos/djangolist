from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.views.generic.base import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('', TemplateView.as_view(template_name='homepage.html'), name="homepage"),
    path('language/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('auctions/', include('auctions.urls')),
    path('accounts/', include('accounts.urls')),

]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
