from django.urls import path
from .views import (
    prices,

    PriceListView,
    PriceCreateView,
    PriceUpdateView,
    PriceDeleteView
)

app_name = 'prices'  # Изменено с 'prices' на 'delivery' для согласованности

urlpatterns = [
    path('', prices, name='prices'),
    path('create/', PriceCreateView.as_view(), name='price_create'),
    path('<int:pk>/update/', PriceUpdateView.as_view(), name='price_update'),
    path('<int:pk>/delete/', PriceDeleteView.as_view(), name='price_delete'),
]
