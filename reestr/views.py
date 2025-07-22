from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Registry
from vod.models import Driver
from pod.models import Podryad
from car.models import Car
from django.db import models

def index(request):
    # Ваша логика для главной страницы
    return render(request, 'index.html')

@login_required
def dashboard(request):
    user = request.user
    context = {'user_type': 'unknown'}

    # Проверяем профиль водителя
    if hasattr(user, 'driver_profile'):
        profile = user.driver_profile
        flights = Registry.objects.filter(models.Q(driver=profile) | models.Q(driver2=profile)).distinct()
        
        # Получаем закрепленные за водителем машины
        assigned_cars = profile.cars.all()

        context = {
            'user_type': 'driver',
            'profile': profile,
            'flights': flights,
            'assigned_cars': assigned_cars, # <-- Передаем машины в шаблон
        }
    
    # Проверяем профиль подрядчика
    elif hasattr(user, 'contractor_profile'):
        profile = user.contractor_profile
        flights = Registry.objects.filter(pod=profile)
        
        # Получаем всех водителей и машины, связанные с этим подрядчиком
        contractor_drivers = Driver.objects.filter(contractor=profile)
        contractor_cars = Car.objects.filter(contractor=profile)

        context = {
            'user_type': 'contractor',
            'profile': profile,
            'flights': flights,
            'contractor_drivers': contractor_drivers, # <-- Передаем водителей
            'contractor_cars': contractor_cars,       # <-- Передаем машины
        }

    return render(request, 'dashboard.html', context)