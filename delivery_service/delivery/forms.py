from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, Service, Price, Role, Order



class OrderClaimCommentForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['comment', 'claim']
        labels = {
            'comment': _('Комментарий'),
            'claim': _('Претензия'),
        }
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': _('Добавьте комментарий к заказу...'),
                'class': 'form-control',
            }),
            'claim': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': _('Добавьте претензию к заказу...'),
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Если понадобится пользователь
        super().__init__(*args, **kwargs)

        # Если нужно, можно добавить логику по правам пользователя
        # Например, запретить редактировать claim для обычных пользователей
        if self.user and not (self.user.is_staff or self.user.is_superuser):
            # Например, запретить редактировать claim
            # self.fields['claim'].disabled = True
            pass

    def clean(self):
        cleaned_data = super().clean()
        # Дополнительная валидация, если нужна
        return cleaned_data

class UserAndOrderForm(forms.Form):
    # Поля пользователя
    name = forms.CharField(
        label='Имя*',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя'
        })
    )
    phone = forms.CharField(
        label='Телефон*',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+79991234567'
        })
    )
    password1 = forms.CharField(
        label='Пароль*',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        }),

    )
    password2 = forms.CharField(
        label='Подтверждение пароля*',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        }),
        help_text="Для подтверждения введите, пожалуйста, пароль ещё раз."
    )

    # Поля заказа
    courier = forms.ModelChoiceField(
        label='Курьер',
        queryset=CustomUser.objects.filter(role__id=2, is_ready=True),  # Фильтр по роли курьера и готовности
        required=False,
        empty_label="--- Выберите курьера ---",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    service = forms.ModelChoiceField(
        label='Услуга',
        queryset=Service.objects.all(),
        required=False,
        empty_label="--- Выберите услугу ---",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    sender_address = forms.CharField(
        label='Адрес отправки',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите адрес отправки'
        })
    )
    recipient_address = forms.CharField(
        label='Адрес получателя',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите адрес получателя'
        })
    )
    order_description = forms.CharField(
        label='Описание заказа',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Опишите заказ'
        })
    )

    def __init__(self, *args, **kwargs):
        self.couriers = CustomUser.objects.filter(role__id=2, is_ready=True)
        self.services = Service.objects.all()
        super().__init__(*args, **kwargs)

        # Настройка отображения курьеров с телефоном
        self.fields['courier'].label_from_instance = lambda obj: f"{obj.name} ({obj.phone})"

        # Настройка отображения услуг с ценой
        self.fields['service'].label_from_instance = lambda obj: f"{obj.name} ({obj.price} руб.)"

        # Автоматическое заполнение стоимости при выборе услуги
        if 'data' in kwargs and kwargs['data'].get('service'):
            try:
                service_id = int(kwargs['data'].get('service'))
                service = Service.objects.get(id=service_id)
                if service.price:
                    self.initial['cost'] = service.price
            except (ValueError, Service.DoesNotExist):
                pass

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'sender', 'courier', 'service', 'sender_address', 'recipient_address',
            'order_description', 'cost', 'status', 'comment', 'claim'
        ]
        labels = {
            'sender': _('Отправитель'),
            'courier': _('Курьер'),
            'service': _('Услуга'),
            'sender_address': _('Адрес отправки'),
            'recipient_address': _('Адрес получателя'),
            'order_description': _('Описание заказа'),
            'cost': _('Стоимость'),
            'status': _('Статус'),
            'comment': _('Комментарий'),
            'claim': _('Претензия'),
        }
        help_texts = {
            'cost': _('Стоимость берется из услуги'),
            'status': _('Текущий статус заказа'),
        }

    def __init__(self, *args, **kwargs):
        courier_queryset = kwargs.pop('courier_queryset', None)
        user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        # Настраиваем queryset для курьеров
        if courier_queryset is not None:
            self.fields['courier'].queryset = courier_queryset
        else:
            self.fields['courier'].queryset = CustomUser.objects.filter(role__id=2, is_ready=True)

        # Кастомные метки для выбора курьера и услуги
        self.fields['courier'].label_from_instance = lambda obj: f"{obj.name} ({obj.phone})"
        self.fields['service'].label_from_instance = lambda obj: f"{obj.name} ({obj.price} руб.)"

        # Для обычных пользователей скрываем поле sender и статус, делаем sender неизменяемым
        if user and not (user.is_staff or user.is_superuser):
            # Ограничиваем sender только текущим пользователем
            self.fields['sender'].queryset = CustomUser.objects.filter(id=user.id)
            self.fields['sender'].initial = user
            self.fields['sender'].disabled = True

            # Скрываем поле status — удаляем из формы
            if 'status' in self.fields:
                self.fields.pop('status')

            # Можно также скрыть поля comment и claim, если нужно
            # self.fields.pop('comment', None)
            # self.fields.pop('claim', None)

        # Для персонала и суперпользователей оставляем все поля доступными

    def clean(self):
        cleaned_data = super().clean()
        # Если пользователь не персонал, принудительно устанавливаем статус 'create'
        user = getattr(self, 'user', None)
        if user and not (user.is_staff or user.is_superuser):
            cleaned_data['status'] = 'create'
        return cleaned_data

class AssignCourierForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['courier']
        labels = {
            'courier': _('Выберите курьера'),
        }

class CourierForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['phone', 'name', 'is_ready']
        labels = {
            'phone': _('Телефон'),
            'name': _('Имя'),
            'is_ready': _('Готов к работе'),
        }
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('+79991234567')
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Иван Иванов')
            }),
            'is_ready': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CourierCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': _('Введите пароль'),
            'autocomplete': 'new-password'
        }),
        help_text=_("""
            <ul class="password-help-text">
                <li>Пароль не должен быть слишком похож на другую вашу личную информацию.</li>
                <li>Ваш пароль должен содержать как минимум 8 символов.</li>
                <li>Пароль не должен быть слишком простым и распространенным.</li>
                <li>Пароль не может состоять только из цифр.</li>
            </ul>
        """)
    )

    password2 = forms.CharField(
        label=_("Подтверждение пароля"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': _('Повторите пароль'),
            'autocomplete': 'new-password'
        }),
        help_text=_("Введите тот же пароль для подтверждения")
    )

    class Meta:
        model = CustomUser
        fields = ['phone', 'name', 'password1', 'password2', 'is_ready']
        labels = {
            'phone': _('Телефон'),
            'name': _('Имя'),
            'is_ready': _('Готов к работе'),
        }
        help_texts = {
            'phone': _('Формат: +79991234567'),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = Role.objects.get(id=2)  # Роль курьера
        if commit:
            user.save()
        return user

class PriceForm(forms.ModelForm):
    class Meta:
        model = Price
        fields = ['service', 'price_value', 'price_list']
        labels = {
            'service': _('Услуга'),
            'price_value': _('Стоимость'),
            'price_list': _('Прайс-лист'),
        }
        widgets = {
            'service': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': _('Выберите услугу')
            }),
            'price_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('Введите стоимость')
            }),
            'price_list': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': _('Выберите прайс-лист')
            }),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price']
        labels = {
            'name': _('Название услуги'),
            'description': _('Описание услуги'),
            'price': _('Цена'),
        }
        help_texts = {
            'description': _('Подробное описание услуги для клиентов'),
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Экспресс-доставка')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Описание услуги...')
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('0.00')
            }),
        }

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('phone', 'name')
        labels = {
            'phone': _('Телефон'),
            'name': _('Имя'),
        }

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('phone', 'name')
        labels = {
            'phone': _('Телефон'),
            'name': _('Имя'),
        }

class PhoneAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Номер телефона"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('+79991234567'),
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Ваш пароль'),
            'autocomplete': 'current-password'
        })
    )