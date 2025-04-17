"""
URL configuration for delivery_service project.
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView
from delivery.views import (home,
    services,
    prices,
    register,
    profile,
    login_view  # Импортируем login_view из delivery.views
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('services/', services, name='services'),
    path('prices/', prices, name='prices'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),  # Используем функцию login_view
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('profile/', profile, name='profile'),
]