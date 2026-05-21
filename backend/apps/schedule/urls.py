from django.urls import path
from . import views

urlpatterns = [
    path('', views.ScheduleListCreateView.as_view(), name='schedule-list-create'),
    path('months/', views.ScheduleMonthsView.as_view(), name='schedule-months'),
    path('periods/<int:year>/<int:month>/toggle/', views.SchedulePeriodToggleView.as_view()),
    path('household/', views.HouseholdSupplyRequestListCreateView.as_view()),
    path('<int:pk>/', views.ScheduleRetrieveUpdateDestroyView.as_view(), name='schedule-detail'),
    path('export/', views.ScheduleExportView.as_view(), name='schedule-export'),
    path('import/', views.ScheduleImportView.as_view(), name='schedule-import'),
]
