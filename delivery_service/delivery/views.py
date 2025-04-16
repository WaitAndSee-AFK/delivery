from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from delivery.forms import CustomUserCreationForm
from .models import Service, Price

# Create your views here.


# Create your views here.
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