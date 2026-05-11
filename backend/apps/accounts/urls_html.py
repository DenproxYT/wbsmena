from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterPageView.as_view(), name='register_page'),
    path('login/', views.LoginPageView.as_view(), name='login_page'),
    path('profile/', views.ProfilePageView.as_view(), name='profile_page'),
    path('first-login/', views.FirstLoginPageView.as_view(), name='first_login_page'),
    path('employees/', views.EmployeesPageView.as_view(), name='employees_page'),
    path('logout/', views.LogoutView.as_view(), name='logout_page'),
]
