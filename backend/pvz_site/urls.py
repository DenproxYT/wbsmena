from django.urls import path, include
from django.contrib import admin

import pvz_site.admin  # noqa: F401 — заголовки и регистрация моделей
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls_html')),
    path('api/accounts/', include('apps.accounts.urls')),
    path('training/', include('apps.training.urls_html')),
    path('schedule/', include('apps.schedule.urls_html')),
    path('api/schedule/', include('apps.schedule.urls')),
    path('api/training/', include('apps.training.urls')),
    path('feedback/', include('apps.core.urls_html')),
    path('api/core/', include('apps.core.urls')),
    path('notifications/', include('apps.core.urls_notifications_html')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
