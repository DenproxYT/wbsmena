from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.NotificationListView.as_view(), name='notifications-list'),
    path('notifications/unread-count/', views.NotificationUnreadCountView.as_view()),
    path('notifications/<int:pk>/read/', views.NotificationMarkReadView.as_view()),
    path('notifications/read-all/', views.NotificationMarkAllReadView.as_view()),
    path('notifications/broadcast/', views.AnnouncementBroadcastView.as_view()),
    path('feedback/', views.FeedbackListCreateView.as_view()),
    path('feedback/<int:pk>/', views.FeedbackDetailView.as_view()),
]
