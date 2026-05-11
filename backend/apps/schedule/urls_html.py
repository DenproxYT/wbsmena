from django.urls import path
from .views_html import SchedulePageView

urlpatterns = [
    path('', SchedulePageView.as_view(), name='schedule_page'),
]
