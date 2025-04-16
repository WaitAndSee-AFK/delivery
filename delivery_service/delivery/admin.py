from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Role, CustomUser, Service, PriceList, Price

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
    readonly_fields = ('created_at',)  # Запрещаем редактирование даты создания
    fieldsets = (
        (None, {
            'fields': ('number', 'is_active')
        }),
        ('Даты действия', {
            'fields': ('created_at', 'valid_until'),
            'description': 'Дата создания устанавливается автоматически'
        }),
    )

# Регистрация модели Service с другим именем класса
@admin.register(Service)
class ServiceModelAdmin(admin.ModelAdmin):  # Изменили имя класса
    list_display = ('name', 'description', 'price')
    search_fields = ('name', 'description')
    list_editable = ('price',)

# Регистрация модели Role
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Кастомная конфигурация для модели пользователя
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)