from django.urls import path
from .views_html import SchedulePageView, HouseholdRequestsAdminPageView

urlpatterns = [
    path('', SchedulePageView.as_view(), name='schedule_page'),
    path('household-requests/', HouseholdRequestsAdminPageView.as_view(), name='household_requests_admin'),
]
