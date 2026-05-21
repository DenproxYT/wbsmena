from django.urls import path
from . import views_html

urlpatterns = [
    path('', views_html.FeedbackPageView.as_view(), name='feedback_page'),
    path('admin/', views_html.FeedbackAdminPageView.as_view(), name='feedback_admin_page'),
]
