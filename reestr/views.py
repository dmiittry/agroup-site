from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q

from reestr.models import Registry
from vod.models import Driver
from pod.models import Podryad
from car.models import Car

# Импортируйте формы редактирования
from vod.forms import DriverProfileForm
from pod.forms import PodryadProfileForm
from vod.forms import DriverSignupForm
from pod.forms import PodryadSignupForm

def index(request):
    return render(request, 'index.html')

@login_required
def dashboard(request):
    user = request.user
    context = {'user_type': 'unknown'}

    # --- ЛК ВОДИТЕЛЯ ---
    if hasattr(user, 'driver_profile'):
        profile = user.driver_profile
        flights = Registry.objects.filter(
            Q(driver=profile) | Q(driver2=profile)
        ).distinct().select_related('marsh', 'gruz', 'number')

        total_flights = flights.count()
        total_tonn = flights.aggregate(s=Sum('tonn'))['s'] or 0
        total_gsm = flights.aggregate(s=Sum('gsm'))['s'] or 0

        context.update({
            'user_type': 'driver',
            'profile': profile,
            'flights': flights,
            'total_flights': total_flights,
            'total_tonn': total_tonn,
            'total_gsm': total_gsm,
        })
        return render(request, 'dashboard.html', context)

    # --- ЛК ПОДРЯДЧИКА ---
    elif hasattr(user, 'contractor_profile'):
        profile = user.contractor_profile
        flights = Registry.objects.filter(
            pod=profile
        ).select_related('driver', 'driver2', 'number', 'marsh', 'gruz').order_by('-dataPOPL')

        total_flights = flights.count()
        total_tonn = flights.aggregate(s=Sum('tonn'))['s'] or 0
        total_gsm = flights.aggregate(s=Sum('gsm'))['s'] or 0

        contractor_drivers = profile.drivers.all().order_by('full_name')
        contractor_cars = profile.cars.all().order_by('number')

        context.update({
            'user_type': 'contractor',
            'profile': profile,
            'flights': flights,
            'total_flights': total_flights,
            'total_tonn': total_tonn,
            'total_gsm': total_gsm,
            'contractor_drivers': contractor_drivers,
            'contractor_cars': contractor_cars,
        })
        return render(request, 'dashboard.html', context)

    # Если профиль не найден
    return render(request, 'dashboard.html', context)


# === Редактирование профиля ВОДИТЕЛЯ ===
@login_required
def profile_edit(request):
    user = request.user
    if not hasattr(user, 'driver_profile'):
        return redirect('dashboard')
    profile = user.driver_profile

    if request.method == 'POST':
        form = DriverProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = DriverProfileForm(instance=profile)

    return render(request, 'profile_edit.html', {'form': form})


# === Редактирование профиля ПОДРЯДЧИКА ===
@login_required
def podryad_profile_edit(request):
    user = request.user
    if not hasattr(user, 'contractor_profile'):
        return redirect('dashboard')
    profile = user.contractor_profile

    if request.method == 'POST':
        form = PodryadProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PodryadProfileForm(instance=profile)

    return render(request, 'podryad_profile_edit.html', {'form': form})


def driver_signup(request):
    if request.method == 'POST':
        form = DriverSignupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'signup_success.html', {'role': 'driver'})
    else:
        form = DriverSignupForm()
    return render(request, 'driver_signup.html', {'form': form})

def podryad_signup(request):
    if request.method == 'POST':
        form = PodryadSignupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'signup_success.html', {'role': 'contractor'})
    else:
        form = PodryadSignupForm()
    return render(request, 'podryad_signup.html', {'form': form})