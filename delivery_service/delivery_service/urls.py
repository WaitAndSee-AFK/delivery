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
    courier_create,
    courier_toggle_status,
    courier_edit,
    courier_delete,
    OrderCreateView,
    OrderUpdateView,
    AssignCourierView,
    create_user_and_order,
    OrderDeleteView,
    OrderEditViewUser,
order_work_view,
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

    path('services/', include('delivery.urls', namespace='delivery')),
    path('prices/', include('delivery.urls_price', namespace='prices')),

    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/edit/', OrderUpdateView.as_view(), name='order_edit'),
    path('orders/<int:pk>/edit/user/', OrderEditViewUser.as_view(), name='order_edit_user'),  # <-- Добавлено здесь
    path('orders/<int:pk>/assign-courier/', AssignCourierView.as_view(), name='order_assign_courier'),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view(), name='order_delete'),

    path('create-user-and-order/', create_user_and_order, name='create_user_and_order'),

path('orders/<int:pk>/work/', order_work_view, name='order_work'),
]
