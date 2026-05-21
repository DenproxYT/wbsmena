from django.urls import path
from . import views_html

urlpatterns = [
    path('send/', views_html.NotificationsAdminPageView.as_view(), name='notifications_send_page'),
]
