from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Role, CustomUser
# Register your models here.

# Регистрация модели Role
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# Кастомная конфигурация для модели пользователя
class CustomUserAdmin(UserAdmin):
    # Поля для отображения в списке пользователей
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_staff')

    # Поля для фильтрации
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    # Группировка полей при редактировании
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    # Поля при создании пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2'),
        }),
    )

    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    ordering = ('username',)


# Регистрация модели CustomUser
admin.site.register(CustomUser, CustomUserAdmin)