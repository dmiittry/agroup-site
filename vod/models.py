from django.db import models # type: ignore
from car.models import Car
from pod.models import Podryad

class Driver(models.Model):
    is_approved = models.BooleanField("Статус согласования", default=False)

    cars = models.ManyToManyField(
        Car,
        blank=True,
        verbose_name='Закрепленные ТС',
        related_name='drivers',
    )
    
    contractor = models.ForeignKey(
        Podryad, on_delete=models.SET_NULL, null=True, blank=True, related_name='drivers',
        verbose_name='Подрядчик'
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

    phone_1 = models.CharField("Номер телефона 1", max_length=20, blank=True, null=True, help_text="89147776655")
    phone_2 = models.CharField("Номер телефона 2", max_length=20, blank=True, null=True, help_text="Если есть второй номер")
    phone_3 = models.CharField("Номер телефона 3", max_length=20, blank=True, null=True, help_text="Если есть третий номер")

    photo1 = models.ImageField("Фото водителя", upload_to='photos/drivers/', blank=True, null=True)
    photo2 = models.ImageField("Фото ВУ спереди", upload_to='photos/drivers/', blank=True, null=True)
    photo21 = models.ImageField("Фото ВУ сзади", upload_to='photos/drivers/', blank=True, null=True)
    photo3 = models.ImageField("Фото СНИЛСА", upload_to='photos/drivers/', blank=True, null=True)
    photo4 = models.ImageField("Фото Паспорта", upload_to='photos/drivers/', blank=True, null=True)
    photo5 = models.ImageField("Фото Паспорта, прописка", upload_to='photos/drivers/', blank=True, null=True)

    def __str__(self):
        return self.full_name or "Без имени"
    
    class Meta:
        verbose_name = "Водитель"
        verbose_name_plural = "Водители"
