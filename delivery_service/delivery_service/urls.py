from django.contrib import admin
from django.urls import path, include
from delivery.views import home, register, profile, login_view, orders
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', profile, name='profile'),
    path('orders/', orders, name='orders'),

    path('services/', include('delivery.urls', namespace='delivery')),
    path('prices/', include('delivery.urls_price', namespace='prices')),
]

    # Подключение маршрутов услуг и цен под одним пространством имен 'delivery'
    # path('services/', include('delivery.urls')),
    # path('prices/', include('delivery.urls_price')),

