from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Role, CustomUser, Service, PriceList, Price, Order, CompletedOrder
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(CompletedOrder)
class CompletedOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'courier', 'service', 'cost', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'service', 'courier')
    search_fields = (
        'sender__name',
        'courier__name',
        'service__name',
        'sender_address',
        'recipient_address',
        'order_description',
        'comment',
        'claim'
    )
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': (
                'sender',
                'courier',
                'service',
                'sender_address',
                'recipient_address',
                'order_description',
                'cost',
                'status',
                'comment',
                'claim',
            )
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        """Запрещаем создание выполненных заказов вручную"""
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'courier', 'service', 'cost', 'status', 'created_at')  # Добавили courier
    list_filter = ('status', 'created_at', 'service', 'courier')  # Добавили courier в фильтры
    search_fields = (
        'sender__name',
        'courier__name',  # Добавили поиск по имени курьера
        'service__name',
        'sender_address',
        'recipient_address',
        'order_description',
        'comment',  # Добавили поиск по комментарию
        'claim'     # Добавили поиск по претензии
    )
    readonly_fields = ('created_at',)

    # Для удобства можно добавить поля в форму редактирования
    fieldsets = (
        (None, {
            'fields': (
                'sender',
                'courier',
                'service',
                'sender_address',
                'recipient_address',
                'order_description',
                'cost',
                'status',
                'comment',
                'claim',
            )
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )



@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('service', 'price_value', 'price_list', 'created_at')
    list_filter = ('price_list', 'service')
    search_fields = ('service__name', 'price_list__number')
    list_editable = ('price_value',)
    readonly_fields = ('created_at',)


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = ('number', 'created_at', 'valid_until', 'is_active')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('number', 'is_active')
        }),
        ('Даты действия', {
            'fields': ('created_at', 'valid_until'),
            'description': 'Дата создания устанавливается автоматически'
        }),
    )


@admin.register(Service)
class ServiceModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price')
    search_fields = ('name', 'description')
    list_editable = ('price',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ('phone', 'name', 'role', 'is_ready', 'is_staff')  # Добавлено is_ready
    list_filter = ('role', 'is_ready', 'is_staff', 'is_superuser', 'is_active')  # Добавлен фильтр по is_ready

    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Персональная информация', {'fields': ('name', 'email', 'role', 'is_ready')}),  # Добавлено is_ready
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'name', 'role', 'password1', 'password2', 'is_ready'),  # Добавлено is_ready
        }),
    )

    search_fields = ('phone', 'name', 'role__name')
    ordering = ('phone',)
    filter_horizontal = ('groups', 'user_permissions',)


admin.site.register(CustomUser, CustomUserAdmin)
