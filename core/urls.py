from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:login'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register_visitor, name='register'),
    path('return/<int:visitor_id>/', views.return_device, name='return_device'),
    path('api/upload/', views.api_upload_log, name='api_upload'),
]