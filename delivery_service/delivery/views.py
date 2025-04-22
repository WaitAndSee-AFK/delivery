from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponsePermanentRedirect,
    HttpResponseForbidden,
    JsonResponse,
)
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView,
    ListView,
)
from django.urls import reverse_lazy
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
import json

from .models import (
    CustomUser,
    Role,
    Order,
    CompletedOrder,
    Service,
    Price,
)
from .forms import (
    CustomUserCreationForm,
    CourierForm,
    CourierCreationForm,
    OrderForm,
    AssignCourierForm,
    UserAndOrderForm,
    OrderClaimCommentForm,
    ServiceForm,
    PriceForm,
)
from django.contrib.auth.hashers import make_password




# Create your views here.
@receiver(post_save, sender=Order)
def transfer_to_completed_orders(sender, instance, created, **kwargs):
    """
    Переносит заказ в таблицу выполненных заказов и удаляет из основной таблицы,
    когда статус становится 'delivered', 'not_delivered' или 'cancelled'
    """
    # Список статусов, при которых заказ переносится
    completed_statuses = ['delivered', 'not_delivered', 'cancelled']

    # Проверяем, что статус изменился на завершающий и это не создание нового объекта
    if instance.status in completed_statuses and not created:
        try:
            with transaction.atomic():
                # Собираем данные для создания CompletedOrder
                order_data = {}
                for field in Order._meta.fields:
                    if field.name == 'id':
                        continue  # id не копируем, он создастся автоматически
                    value = getattr(instance, field.name)
                    order_data[field.name] = value

                # Создаем выполненный заказ
                completed_order = CompletedOrder.objects.create(**order_data)

                # Удаляем оригинальный заказ
                instance.delete()

                print(f"Заказ {instance.id} перенесён в CompletedOrder с ID {completed_order.id}")

        except Exception as e:
            print(f"Ошибка при переносе заказа {instance.id}: {e}")
            raise


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

            return redirect('orders')
    else:
        form = UserAndOrderForm()

    context = {
        'form': form,
        'couriers': CustomUser.objects.filter(role__id=2, is_ready=True),
        'services': Service.objects.all(),
    }
    return render(request, 'delivery/create_user_and_order.html', context)




class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'delivery/order_form.html'
    success_url = reverse_lazy('orders')  # Используется по умолчанию, но мы переопределим в form_valid

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'courier_queryset': CustomUser.objects.filter(role__id=2, is_ready=True),
            'user': self.request.user,  # Передаём пользователя в форму
        })
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        service_id = self.request.GET.get('service_id')
        if service_id:
            initial['service'] = service_id
        initial['courier'] = None  # Устанавливаем courier в None по умолчанию
        return initial

    def form_valid(self, form):
        # Для обычных пользователей автоматически устанавливаем sender и статус
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            form.instance.sender = self.request.user
            form.instance.status = 'create'  # Устанавливаем статус "Создан"
        response = super().form_valid(form)

        # Редирект в зависимости от роли пользователя
        if self.request.user.is_staff or self.request.user.is_superuser:
            return redirect('orders')  # Страница со списком заказов для персонала
        else:
            return redirect('profile')  # Страница профиля для обычных пользователей

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_id = self.request.GET.get('service_id')
        if service_id:
            try:
                context['selected_service'] = Service.objects.get(id=service_id)
            except Service.DoesNotExist:
                pass
        return context




class OrderEditViewUser(LoginRequiredMixin, View):
    template_name = 'delivery/order_form.html'

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, sender=request.user)
        form = OrderForm(instance=order, user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, sender=request.user)
        form = OrderForm(request.POST, instance=order, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, self.template_name, {'form': form})



class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'delivery/order_form.html'
    success_url = reverse_lazy('orders')

    def get_form_kwargs(self):
        """Передаем отфильтрованный queryset для курьеров в форму"""
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'courier_queryset': CustomUser.objects.filter(role__id=2, is_ready=True)
        })
        return kwargs

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
def order_work_view(request, pk):
    order = get_object_or_404(Order, pk=pk)

    # Проверяем, что текущий пользователь — курьер этого заказа или персонал
    user = request.user
    user_role_id = getattr(user.role, 'id', None)
    if order.courier != user and not user.is_staff:
        return HttpResponseForbidden("У вас нет доступа к этому заказу.")

    if request.method == 'POST':
        form = OrderClaimCommentForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('courier_deliveries')  # или на другую страницу по вашему выбору
    else:
        form = OrderClaimCommentForm(instance=order)

    return render(request, 'delivery/order_work.html', {'order': order, 'form': form})


@login_required
def courier_deliveries(request):
    user = request.user

    # Проверяем, что пользователь — курьер (роль id=2) или персонал
    user_role_id = getattr(user.role, 'id', None)
    if user_role_id != 2 and not user.is_staff:
        return HttpResponseForbidden("У вас нет доступа к этой странице.")

    # Если пользователь — курьер (не персонал), показываем только его заказы
    if user_role_id == 2 and not user.is_staff:
        orders = Order.objects.filter(courier=user).order_by('-created_at')
    else:
        # Для персонала показываем все заказы
        orders = Order.objects.all().order_by('-created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'delivery/deliveries.html', context)


def staff_or_superuser_check(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

class OrderDeleteView(DeleteView):
    model = Order
    template_name = 'delivery/order_confirm_delete.html'
    success_url = reverse_lazy('orders')

@login_required
@user_passes_test(staff_or_superuser_check)
def orders(request):
    active_orders = Order.objects.select_related('sender', 'courier', 'service').exclude(
        status__in=['delivered', 'not_delivered', 'cancelled']
    ).order_by('-created_at')

    completed_orders = CompletedOrder.objects.select_related('sender', 'courier', 'service').all().order_by(
        '-created_at')

    return render(request, 'delivery/orders.html', {
        'active_orders': active_orders,
        'completed_orders': completed_orders
    })

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
