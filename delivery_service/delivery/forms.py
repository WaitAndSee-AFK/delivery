from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser
from .models import Service
from .models import Price
from .models import CustomUser, Role
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Role

class CourierForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['phone', 'name', 'is_ready', 'role']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_ready': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'role': forms.Select(attrs={'class': 'form-select'}),

        }

class CourierCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите пароль'
        }),
        help_text="Пароль должен содержать минимум 8 символов"
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Повторите пароль'
        }),
        help_text="Введите тот же пароль для подтверждения"
    )

    class Meta:
        model = CustomUser
        fields = ['phone', 'name', 'password1', 'password2', 'is_ready']

class PriceForm(forms.ModelForm):
    class Meta:
        model = Price
        fields = ['service', 'price_value', 'price_list']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'price_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_list': forms.Select(attrs={'class': 'form-control'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price']  # добавьте все необходимые поля
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('phone', 'name')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('phone', 'name')

class PhoneAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Номер телефона")