from django.db import models # type: ignore
from car.models import Car
from pod.models import Podryad
from django.contrib.auth.models import User

class DriverPhoto(models.Model):
    driver = models.ForeignKey(
        'Driver',
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name="Водитель"
    )
    image = models.ImageField("Фото", upload_to='photos/driver_album/')
    description = models.CharField("Краткое описание", max_length=255, blank=True)

    class Meta:
        verbose_name = "Фотография водителя"
        verbose_name_plural = "Фотографии водителя"

    def __str__(self):
        return f"Фото для {self.driver.full_name}"
    
class Driver(models.Model):
    can_login = models.BooleanField("Доступ к личному кабинету", default=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile', null=True, blank=True)
    is_approved = models.BooleanField("Статус согласования СБ", default=False)

    cars = models.ManyToManyField(
        Car,
        blank=True,
        verbose_name='Закрепленные ТС',
        related_name='drivers',
        help_text='Выберите закрепленные транспортные средства'
    )
    
    full_name = models.CharField("ФИО", max_length=255, help_text="ФИО Полностью")
    birth_date = models.DateField("Дата рождения", blank=True, null=True)
    driver_license = models.CharField("Номер водительского удостоверения (ВУ)", max_length=50, blank=True, null=True)
    vy_date = models.DateField("Дата выдачи ВУ", blank=True, null=True)
    snils = models.CharField("СНИЛС", max_length=20, blank=True, null=True)

    issued_by = models.TextField("Паспорт: Кем выдан", blank=True, null=True)
    issue_date = models.DateField("Дата выдачи", blank=True, null=True)
    number = models.CharField("Номер паспорта", max_length=20, blank=True, null=True)
    series = models.CharField("Серия паспорта", max_length=20, blank=True, null=True)
    registration = models.TextField("Прописка", blank=True, null=True)
    dopog = models.BooleanField("Наличие ДОПОГа", default=False)

    phone_1 = models.CharField("Номер телефона 1", max_length=20, blank=True, null=True, help_text="89147776655")
    phone_2 = models.CharField("Номер телефона 2", max_length=20, blank=True, null=True, help_text="Если есть второй номер")
    phone_3 = models.CharField("Номер телефона 3", max_length=20, blank=True, null=True, help_text="Если есть третий номер")

    def __str__(self):
        return self.full_name or "Без имени" 
    
    class Meta:
        verbose_name = "Водитель"
        verbose_name_plural = "Водители"