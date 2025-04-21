from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from delivery.forms import CustomUserCreationForm
from django.contrib.auth.views import LoginView
from .models import Service, Price
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, CreateView
from django.urls import reverse_lazy
from .forms import ServiceForm, PriceForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, HttpResponseForbidden
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import CustomUser, Role
from .models import Order
from .forms import CourierForm, CourierCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Order
from .forms import OrderForm, AssignCourierForm
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm, OrderForm
from django.shortcuts import render, redirect
from .forms import UserAndOrderForm


# Create your views here.

from django.shortcuts import render, redirect
from .forms import UserAndOrderForm
from .models import CustomUser, Service, Order
from django.contrib.auth.hashers import make_password

def create_user_and_order(request):
    if request.method == 'POST':
        form = UserAndOrderForm(request.POST)
        if form.is_valid():
            # Создание пользователя
            user = CustomUser.objects.create(
                name=form.cleaned_data['name'],
                phone=form.cleaned_data['phone'],
                password=make_password(form.cleaned_data['password1']),
                role_id = 1 # Set default role id
            )

            # Создание заказа
            order = Order.objects.create(
                sender=user,  # Указываем созданного пользователя как отправителя
                courier=form.cleaned_data['courier'],
                service=form.cleaned_data['service'],
                sender_address=form.cleaned_data['sender_address'],
                recipient_address=form.cleaned_data['recipient_address'],
                order_description=form.cleaned_data['order_description']
            )

            return redirect('orders')  # Замените 'success_url' на URL вашей страницы успеха
    else:
        form = UserAndOrderForm()

    context = {
        'form': form,
        'user_form': UserAndOrderForm(prefix='user'),
        'order_form': UserAndOrderForm(prefix='order'),
        'couriers': CustomUser.objects.filter(role__id=2, is_ready=True),
        'services': Service.objects.all(),
    }
    return render(request, 'delivery/create_user_and_order.html', context)


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'delivery/order_form.html'  # Создайте этот шаблон
    success_url = reverse_lazy('orders')  # URL списка заказов

    def form_valid(self, form):
        # Дополнительная логика при создании заказа
        return super().form_valid(form)


class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'delivery/order_form.html'  # Создайте этот шаблон
    success_url = reverse_lazy('orders')  # URL списка заказов


class AssignCourierView(View):
    template_name = 'delivery/assign_courier.html'  # Создайте этот шаблон

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        form = AssignCourierForm(instance=order)
        return render(request, self.template_name, {'form': form, 'order': order})

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        form = AssignCourierForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('orders')  # URL списка заказов
        return render(request, self.template_name, {'form': form, 'order': order})


def is_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(is_admin)
def admin_couriers(request):
    couriers = CustomUser.objects.filter(role__name='Курьер').order_by('-date_joined')
    return render(request, 'delivery/admin_couriers.html', {'couriers': couriers})

@user_passes_test(is_admin)
def courier_create(request):
    if request.method == 'POST':
        form = CourierCreationForm(request.POST)
        if form.is_valid():
            courier = form.save()
            return redirect('admin_couriers')
    else:
        form = CourierCreationForm()
    return render(request, 'delivery/courier_form.html', {'form': form})


@user_passes_test(is_admin)
def courier_edit(request, pk):
    courier = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = CourierForm(request.POST, instance=courier)
        if form.is_valid():
            courier = form.save()
            return redirect('admin_couriers')
    else:
        form = CourierForm(instance=courier)
    return render(request, 'delivery/courier_form.html', {'form': form})

@user_passes_test(is_admin)
def courier_delete(request, pk):
    courier = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        courier.delete()
        return redirect('admin_couriers')
    return render(request, 'delivery/courier_confirm_delete.html', {'courier': courier})

@require_POST
@login_required
def courier_toggle_status(request):
    if request.user.role.id != 2:  # Проверяем, что пользователь - курьер
        return JsonResponse({'success': False, 'error': 'Доступ запрещен'}, status=403)

    try:
        data = json.loads(request.body)
        is_ready = data.get('is_ready', False)

        # Обновляем статус курьера
        request.user.is_ready = is_ready
        request.user.save()

        return JsonResponse({
            'success': True,
            'is_ready': is_ready,
            'message': f'Статус изменен на {"Готов" if is_ready else "Не готов"}'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def courier_deliveries(request):
    # Проверяем, что пользователь - курьер или персонал
    if not (request.user.role.id == 2 or request.user.is_staff):
        return HttpResponseForbidden()

    # Логика для страницы "Мои доставки"
    return render(request, 'courier/deliveries.html')

def staff_or_superuser_check(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)



@login_required
@user_passes_test(staff_or_superuser_check)
def orders(request):
    orders = Order.objects.select_related('sender', 'service').all().order_by('-created_at')
    return render(request, 'delivery/orders.html', {'orders': orders})

class PriceListView(ListView):
    model = Price
    template_name = 'delivery/prices.html'
    context_object_name = 'prices'

class PriceCreateView(CreateView):
    model = Price
    form_class = PriceForm
    template_name = 'delivery/price_form.html'
    success_url = reverse_lazy('prices')  # Без namespace

class PriceUpdateView(UpdateView):
    model = Price
    form_class = PriceForm
    template_name = 'delivery/price_form.html'
    success_url = reverse_lazy('prices')

class PriceDeleteView(DeleteView):
    model = Price
    template_name = 'delivery/price_confirm_delete.html'
    success_url = reverse_lazy('prices')

class ServiceCreateView(CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'delivery/service_form.html'
    success_url = reverse_lazy('delivery:services')  # Исправлено

class ServiceUpdateView(UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'delivery/service_form.html'
    success_url = reverse_lazy('delivery:services')  # Исправлено

class ServiceDeleteView(DeleteView):
    model = Service
    template_name = 'delivery/service_confirm_delete.html'
    success_url = reverse_lazy('delivery:services')  # Исправлено

class CustomLoginView(LoginView):
    template_name = 'delivery/login.html'  # Укажите правильный путь к шаблону

    def form_valid(self, form):
        phone = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=phone, password=password)

        if user is not None:
            login(self.request, user)
            return redirect('home')
        return super().form_invalid(form)


def login_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        # Проверка данных в консоли (для отладки)
        print(f"Attempting login with phone: {phone}, password: {password}")

        user = authenticate(request, username=phone, password=password)

        if user is not None:
            login(request, user)
            print("Login successful!")  # Отладочное сообщение
            return redirect('home')
        else:
            messages.error(request, 'Неверный номер телефона или пароль')
            print("Login failed!")  # Отладочное сообщение

    return render(request, 'delivery/login.html')

def home(request):
    return render(request, 'home.html')

def services(request):
    services = Service.objects.all()  # Получаем все услуги из базы
    return render(request, 'services.html', {'services': services})

def prices(request):
    # Получаем все цены с предварительной загрузкой связанных услуг
    prices = Price.objects.select_related('service').all()
    return render(request, 'prices.html', {'prices': prices})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    orders = Order.objects.filter(sender=request.user).order_by('-created_at')
    return render(request, 'delivery/profile.html', {'orders': orders})
