from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser
from .models import Service
from .models import Price

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