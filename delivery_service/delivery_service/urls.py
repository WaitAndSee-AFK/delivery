from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from delivery.views import (
    home,
    register,
    profile,
    login_view,
    orders,
    courier_deliveries,
    admin_couriers,
    courier_create,  # Добавлен импорт
    courier_toggle_status,
    courier_edit,
    courier_delete
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', profile, name='profile'),
    path('orders/', orders, name='orders'),

    path('courier/toggle-status/', courier_toggle_status, name='courier_toggle_status'),
    path('couriers/', admin_couriers, name='admin_couriers'),
    path('couriers/create/', courier_create, name='courier_create'),
    path('couriers/<int:pk>/edit/', courier_edit, name='courier_edit'),
    path('couriers/<int:pk>/delete/', courier_delete, name='courier_delete'),
    path('courier/deliveries/', courier_deliveries, name='courier_deliveries'),

    # Подключение других URL-конфигураций
    path('services/', include('delivery.urls', namespace='delivery')),
    path('prices/', include('delivery.urls_price', namespace='prices')),
]