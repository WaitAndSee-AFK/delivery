from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Order(models.Model):
    STATUS_CHOICES = [
        ('courier', 'Доставляет курьер'),
        ('ready_for_pickup', 'Готов к выдаче'),
        ('delivered', 'Вручен'),
        ('partially_delivered', 'Частично вручен'),
        ('not_delivered', 'Не вручен'),
    ]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Отправитель",
        related_name='orders_sent'
    )
    service = models.ForeignKey(
        'Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Услуга",
        related_name='orders'
    )

    sender_address = models.CharField(
        max_length=255,
        verbose_name="Адрес отправки",
        blank=True,
        default=''
    )
    order_description = models.TextField(
        verbose_name="Описание заказа",
        blank=True,
        default=''
    )
    recipient_address = models.CharField(
        max_length=255,
        verbose_name="Адрес получателя",
        blank=True,
        default=''
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Стоимость",
        null=True,
        blank=True,
        help_text="Стоимость берется из услуги"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='courier',
        verbose_name="Статус заказа"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        sender_name = self.sender.name if self.sender else "Неизвестный отправитель"
        service_name = self.service.name if self.service else "Без услуги"
        cost_display = f"{self.cost} руб." if self.cost is not None else "Цена не указана"
        return f"Заказ от {sender_name} — {service_name} — {cost_display}"

    def save(self, *args, **kwargs):
        # Если выбрана услуга и цена в заказе не указана или отличается от цены услуги — обновляем
        if self.service:
            service_price = self.service.price
            if service_price is not None and (self.cost is None or self.cost != service_price):
                self.cost = service_price
        super().save(*args, **kwargs)


class Service(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название услуги")
    description = models.TextField(verbose_name="Описание услуги")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.price} руб.)"

class PriceList(models.Model):
    number = models.CharField(max_length=20, verbose_name="Номер прайса", unique=True)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
        help_text="Автоматически устанавливается при создании"
    )
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        verbose_name="Дата окончания",
        help_text="Оставьте пустым для бессрочного действия"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен"
    )

    class Meta:
        verbose_name = "Прайс-лист"
        verbose_name_plural = "Прайс-листы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Прайс-лист №{self.number} от {self.created_at.strftime('%d.%m.%Y')}"

    def save(self, *args, **kwargs):
        if not self.valid_until:
            self.valid_until = None
        super().save(*args, **kwargs)

class Price(models.Model):
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Услуга",
        related_name='prices'
    )
    price_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Стоимость",
        null=True,
        blank=True
    )
    price_list = models.ForeignKey(
        PriceList,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Прайс-лист",
        related_name='prices'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Цена"
        verbose_name_plural = "Цены"
        ordering = ['-created_at']

    def __str__(self):
        service_name = self.service.name if self.service else "Без услуги"
        price_value = self.price_value if self.price_value is not None else "не указана"
        price_list = self.price_list.number if self.price_list else "без прайса"
        return f"{service_name} - {price_value} руб. (Прайс: {price_list})"

class Role(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название роли")

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def create_user(self, phone, name, password=None, **extra_fields):
        if not phone:
            raise ValueError(_('The Phone must be set'))
        user = self.model(phone=phone, name=name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(phone, name, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None  # Удаляем поле username
    phone = models.CharField(_('Phone'), max_length=20, unique=True)
    name = models.CharField(_('Name'), max_length=100)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']  # Обязательные поля при createsuperuser

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.name} ({self.phone})"