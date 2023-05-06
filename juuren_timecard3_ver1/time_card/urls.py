from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views
from .views import ProfileView, AttendanceCreateView


app_name = 'time_card'

urlpatterns = [
    path('', views.home, name='home'),
    path('attendance/', AttendanceCreateView.as_view(), name='attendance'),
    path('monthly-attendance/', views.monthly_attendance, name='monthly_attendance'),
    path('profile/', ProfileView.as_view(), name='profile'), 
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html', next_page='time_card:login'), name='logout'),
]
