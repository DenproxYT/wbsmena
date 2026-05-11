from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('first-login/', views.FirstLoginCredentialsView.as_view(), name='first-login'),
    path('logout/', views.APILogoutView.as_view(), name='api_logout'),
    path('create/', views.UserCreateByAdminView.as_view(), name='user-create'),
    path('bulk-create/', views.BulkUserCreateByAdminView.as_view(), name='user-bulk-create'),
    path('', views.UserListView.as_view(), name='user-list'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
]
