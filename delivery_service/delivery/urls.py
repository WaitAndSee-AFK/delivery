from django.urls import path
from .views import (
    services,
    ServiceCreateView,
    ServiceUpdateView,
    ServiceDeleteView
)

app_name = 'delivery'

urlpatterns = [
    # Только маршруты для услуг
    path('', services, name='services'),
    path('create/', ServiceCreateView.as_view(), name='service_create'),
    path('<int:pk>/edit/', ServiceUpdateView.as_view(), name='service_edit'),
    path('<int:pk>/delete/', ServiceDeleteView.as_view(), name='service_delete'),
]