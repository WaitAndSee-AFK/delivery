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


# Create your views here.
def staff_or_superuser_check(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
@user_passes_test(staff_or_superuser_check)
def orders(request):
    orders = []
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
    return render(request, 'profile.html', {'user': request.user})