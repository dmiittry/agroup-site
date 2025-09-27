from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404

import openpyxl

from reestr.models import Registry, Season
from vod.models import Driver
from pod.models import Podryad
from car.models import Car

# Импортируем все необходимые формы
from vod.forms import DriverProfileForm, DriverSignupForm, UserChangeForm, DriverPhotoForm, DriverPhoto, DriverPhotoEditForm
from pod.forms import PodryadProfileForm, PodryadSignupForm, ContractorUserChangeForm, PodryadPhotoForm, PodryadPhotoEditForm, PodryadPhoto  
from car.forms import CarForm

def index(request):
    return render(request, 'index.html')
# reestr/views.py (добавьте в конец файла)

@login_required
def car_add(request):
    contractor = getattr(request.user, 'contractor_profile', None)
    if not contractor:
        messages.error(request, "Эта функция доступна только подрядчикам.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            new_car = form.save()
            contractor.cars.add(new_car)          # привязываем к подрядчику
            messages.success(request,
                            f"ТС {new_car.number} успешно добавлено.")
            return redirect('dashboard')
    else:
        form = CarForm()

    return render(request, 'car_add.html', {'form': form})

@login_required
def edit_driver_photo(request, photo_id):  # [4]
    driver = getattr(request.user, 'driver_profile', None)  # [23]
    photo = get_object_or_404(DriverPhoto, id=photo_id, driver=driver)  # [13]
    if request.method == 'POST':  # [4]
        if 'delete' in request.POST:  # обработка удаления [4]
            photo.delete()  # [23]
            messages.success(request, "Фото удалено")  # [6]
            return redirect('dashboard')  # [6]
        form = DriverPhotoEditForm(request.POST, instance=photo)  # [3]
        if form.is_valid():  # [3]
            form.save()  # [3]
            messages.success(request, "Описание обновлено")  # [6]
            return redirect('dashboard')  # [6]
    else:
        form = DriverPhotoEditForm(instance=photo)  # [3]
    return render(request, 'vod_edit_photo.html', {'form': form, 'photo': photo})

@login_required
def add_driver_photo(request):
    driver = getattr(request.user, 'driver_profile', None)
    if not driver or driver.status != 'approved':
        messages.error(request, "Доступ запрещён")
        return redirect('dashboard')  # или другой URL

    if request.method == "POST":
        form = DriverPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.driver = driver
            photo.save()
            messages.success(request, "Фото успешно добавлено")
            return redirect('dashboard')
    else:
        form = DriverPhotoForm()

    return render(request, 'vod_add_photo.html', {'form': form})

@login_required
def edit_podryad_photo(request, photo_id):
    podryad = getattr(request.user, 'contractor_profile', None)
    photo = get_object_or_404(PodryadPhoto, id=photo_id, podryad=podryad)
    if request.method == 'POST':
        if 'delete' in request.POST:
            photo.delete()
            messages.success(request, "Фото удалено")
            return redirect('dashboard')
        form = PodryadPhotoEditForm(request.POST, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, "Описание обновлено")
            return redirect('dashboard')
    else:
        form = PodryadPhotoEditForm(instance=photo)
    return render(request, 'pod_edit_photo.html', {'form': form, 'photo': photo})

@login_required
def add_podryad_photo(request):
    podryad = getattr(request.user, 'contractor_profile', None)
    if not podryad or podryad.status != 'approved':
        messages.error(request, "Доступ запрещён")
        return redirect('dashboard')  # или другой URL

    if request.method == 'POST':
        form = PodryadPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.podryad = podryad
            photo.save()
            messages.success(request, "Фото успешно добавлено")
            return redirect('dashboard')
    else:
        form = PodryadPhotoForm()

    return render(request, 'pod_add_photo.html', {'form': form})

@login_required
def export_flights_to_excel(request):
    user = request.user
    flights = None

    # Определяем, для кого формируем отчет
    if hasattr(user, 'driver_profile'):
        profile = user.driver_profile
        flights = Registry.objects.filter(Q(driver=profile) | Q(driver2=profile)).distinct()
        filename = f"рейсы_водитель_{profile.full_name}.xlsx"
    elif hasattr(user, 'contractor_profile'):
        profile = user.contractor_profile
        flights = Registry.objects.filter(pod=profile)
        filename = f"рейсы_подрядчик_{profile.org_name}.xlsx"
    else:
        # Если профиль не определен, ничего не делаем
        return redirect('dashboard')

    # Создаем HTTP-ответ с типом содержимого для Excel
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Создаем книгу и лист Excel
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Рейсы'

    # Заголовки столбцов
    columns = [
        'Водитель', 'Второй водитель', 'Подрядчик', 'Номер ТС', 'Маршрут',
        'Номер ПЛ', 'Дата выдачи ПЛ', 'Дата сдачи ПЛ', 'Номер ТТН',
        'Дата погрузки груза', 'Дата выгрузки груза', 'Тонн', 'Вид груза', 'ГСМ'
    ]
    worksheet.append(columns)

    # Заполняем строки данными
    for flight in flights:
        row = [
            flight.driver.full_name if flight.driver else '',
            flight.driver2.full_name if flight.driver2 else '',
            flight.pod.org_name if flight.pod else '',
            flight.number.number if flight.number else '',
            flight.marsh.name if flight.marsh else '',
            flight.numberPL,
            flight.dataPOPL.strftime('%d.%m.%Y') if flight.dataPOPL else '',
            flight.dataSDPL.strftime('%d.%m.%Y') if flight.dataSDPL else '',
            flight.numberTN,
            flight.dataPOG.strftime('%d.%m.%Y') if flight.dataPOG else '',
            flight.dataVYG.strftime('%d.%m.%Y') if flight.dataVYG else '',
            flight.tonn,
            flight.gruz.name if flight.gruz else '',
            flight.gsm,
        ]
        worksheet.append(row)

    # Сохраняем книгу в ответ
    workbook.save(response)

    return response

@login_required
def dashboard(request):
    user = request.user

    # Определяем профиль и роль
    driver = getattr(user, 'driver_profile', None)
    contractor = getattr(user, 'contractor_profile', None)
    profile = driver or contractor
    if not profile:
        return render(request, 'dashboard.html', {'user_type': 'unknown'})

    is_driver = driver is not None

    # --- ОБЩАЯ ЛОГИКА ФИЛЬТРАЦИИ ---
    season_id = request.GET.get('season')
    
    if is_driver:
        if profile.status != 'approved':
            return render(request, 'lk_not_allowed.html')
        # Базовый запрос для водителя
        flights_qs = Registry.objects.filter(Q(driver=profile) | Q(driver2=profile)).distinct()
    else:
        # Базовый запрос для подрядчика
        flights_qs = Registry.objects.filter(pod=profile)

    # Применяем фильтр по сезону, если он выбран
    if season_id:
        flights_qs = flights_qs.filter(season_id=season_id)

    # Финальный запрос с подгрузкой связанных данных
    flights = flights_qs.select_related('driver', 'driver2', 'pod', 'number', 'marsh', 'gruz', 'season').order_by('-dataPOPL')

    # --- ОБЩИЙ РАСЧЕТ СТАТИСТИКИ И КОНТЕКСТ ---
    seasons = Season.objects.all().order_by('-name')
    context = {
        'profile': profile,
        'is_driver': is_driver,
        'user_type': 'driver' if is_driver else 'contractor',
        'flights': flights,
        'total_flights': flights.count(),
        'total_completed_flights': flights.filter(tonn__isnull=False).exclude(tonn=0).count(),
        'total_tonn': flights.aggregate(s=Sum('tonn'))['s'] or 0,
        'total_gsm': flights.aggregate(s=Sum('gsm'))['s'] or 0,
        'seasons': seasons,
        'current_season': int(season_id) if season_id else None,
    }

    # Добавляем специфичные для подрядчика данные
    if not is_driver:
        if profile.status != 'approved':
            return render(request, 'lk_not_allowed.html')
        context.update({
            'contractor_drivers': profile.drivers.all().order_by('full_name').prefetch_related('cars'),
            'contractor_cars': profile.cars.all().order_by('number'),
        })

    return render(request, 'dashboard.html', context)


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

@login_required
def user_change_credentials(request):
    user = request.user
    if request.method == "POST":
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            password1 = form.cleaned_data.get('password1')
            if password1:
                user.set_password(password1)
            user.save()
            update_session_auth_hash(request, user)
            return redirect("dashboard")
    else:
        form = UserChangeForm(instance=user)
    return render(request, "user_change_credentials.html", {"form": form})

@login_required
def contractor_change_credentials(request):
    user = request.user
    if not hasattr(user, 'contractor_profile'):
        return redirect('dashboard')
    if request.method == "POST":
        form = ContractorUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            password1 = form.cleaned_data.get('password1')
            if password1:
                user.set_password(password1)
            user.save()
            update_session_auth_hash(request, user)
            return redirect("dashboard")
    else:
        form = ContractorUserChangeForm(instance=user)
    return render(request, "contractor_change_credentials.html", {"form": form})

def custom_404_view(request, exception):
    return render(request, "404.html", status=404)