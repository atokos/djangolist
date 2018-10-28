from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import schedule
import time
import threading

from auctions import jobs
from auctions.api import *
from .views import generate_data, email_history_view


def run_continuosly(sch, interval=1):

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while True:
                sch.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()


schedule.every(1).minutes.do(jobs.resolve_auction_job)
schedule.every(1).minutes.do(jobs.fetch_exchange_rate_job)
run_continuosly(schedule)

urlpatterns = [
    path('', TemplateView.as_view(template_name='homepage.html'), name="homepage"),
    path('language/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('auctions/', include('auctions.urls')),
    path('accounts/', include('accounts.urls')),
    path('api/auctions/', auction_list , name='api-list'),
    path('api/auctions/<int:auction_id>', auction_detail, name='api-detail'),
    path('generatedata/', generate_data, name='generatedata'),
    path('emailhistory/', email_history_view, name='emailhistory'),
]

urlpatterns += staticfiles_urlpatterns()





