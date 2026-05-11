from django.urls import path
from . import views

urlpatterns = [
    path('', views.TrainingListCreateView.as_view(), name='training-list-create'),
    path('progress/', views.TrainingProgressView.as_view(), name='training-progress'),
    path('tests/<int:material_id>/', views.TrainingTestDetailView.as_view(), name='training-test-detail'),
    path('tests/<int:material_id>/attempt/', views.TrainingTestAttemptView.as_view(), name='training-test-attempt'),
    path('stats/', views.TrainingStatsView.as_view(), name='training-stats'),
]

