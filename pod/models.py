from django.db import models # type: ignore
from django.contrib.auth.models import User

class PodryadPhoto(models.Model):
    podryad = models.ForeignKey(
        'Podryad', 
        on_delete=models.CASCADE, 
        related_name='photos',
        verbose_name="Подрядчик"
    )
    image = models.ImageField("Фото", upload_to='photos/podryad_album/')
    description = models.CharField("Краткое описание", max_length=255, blank=True)

    class Meta:
        verbose_name = "Фотография подрядчика"
        verbose_name_plural = "Фотографии подрядчика"

    def __str__(self):
        return f"Фото для {self.podryad.org_name}"

class Podryad(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='contractor_profile', null=True, blank=True)
    org_name = models.CharField("Название организации", max_length=255, help_text="Например: ООО Компания или ИП Иванов Иван Иванович (ФИО Полностью)")
    
    contract_number = models.CharField("Номер договора", max_length=100, blank=True, null=True)

    drivers = models.ManyToManyField(
        'vod.Driver',
        related_name='contractors',
        blank=True,
        verbose_name="Водители"
    )
    cars = models.ManyToManyField(
        'car.Car',
        blank=True,
        related_name='podryads',
        verbose_name='Транспортные средства'
    )

    full_name = models.CharField("ФИО", max_length=255, help_text="ФИО директора полностью", blank=True, null=True)
    birth_date = models.DateField("Дата рождения", blank=True, null=True)
    snils = models.CharField("СНИЛС", max_length=20, blank=True, null=True)

    issued_by = models.TextField("Паспорт: Кем выдан", blank=True, null=True)
    issue_date = models.DateField("Дата выдачи", blank=True, null=True)
    number = models.CharField("Номер паспорта", max_length=20, blank=True, null=True)
    series = models.CharField("Серия паспорта", max_length=20, blank=True, null=True)
    registration = models.TextField("Прописка", blank=True, null=True)
    
    bank = models.CharField("Банк", max_length=30, blank=True, null=True, help_text="Реквизиты организации")
    inn = models.CharField("ИНН", max_length=20, blank=True, null=True)
    kpp = models.CharField("КПП", max_length=20, blank=True, null=True)
    ogrn = models.CharField("ОГРН", max_length=20, blank=True, null=True)
    okpo = models.CharField("ОКПО", max_length=20, blank=True, null=True)
    num_chet = models.CharField("Номер р/счета", max_length=30, blank=True, null=True)
    num_bik = models.CharField("Номер БИК", max_length=30, blank=True, null=True)
    num_corch = models.CharField("Номер корр/сч", max_length=30, blank=True, null=True)
    email = models.CharField("Эл. почта", max_length=30, blank=True, null=True)
    adress = models.TextField("Юридический адрес", blank=True, null=True)

    phone_1 = models.CharField("Номер телефона 1", max_length=20, help_text="89147776655", blank=True, null=True)
    phone_2 = models.CharField("Номер телефона 2", max_length=20, blank=True, null=True, help_text="Если есть второй номер")
    phone_3 = models.CharField("Номер телефона 3", max_length=20, blank=True, null=True, help_text="Можно номер бухгалтера")

    def __str__(self):
        return self.org_name
    
    class Meta:
        verbose_name = "Подрядчик"
        verbose_name_plural = "Подрядчики"
        ordering = ['org_name']
