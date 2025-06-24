from django.db import models # type: ignore
from pod.models import Podryad

class CarModel(models.Model):
    name = models.CharField("Вид ТС", max_length=20)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Вид ТС"
        verbose_name_plural = "Вид ТС"
    
class CarMarka(models.Model):
    name = models.CharField("Марка ТС", max_length=20)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Марка ТС"
        verbose_name_plural = "Марка ТС"

class Car(models.Model):
    is_approved = models.BooleanField("Статус согласования", default=False)
    contractor = models.ForeignKey(
        Podryad, on_delete=models.SET_NULL, null=True, blank=True, related_name='cars',
        verbose_name='Подрядчик'
    )
    # drivers = models.ManyToManyField(
    #     'vod.Driver', blank=True, related_name='cars', verbose_name='Водители'
    # )
    model = models.ForeignKey(
        CarModel,
        on_delete=models.CASCADE,
        verbose_name="Вид ТС",
        help_text="Если нету в списке, то добавьте в разделе Вид ТС",
        related_name='model'
    )
    marka = models.ForeignKey(
        CarMarka,
        on_delete=models.CASCADE,
        verbose_name="Марка ТС",
        help_text="Если нету в списке, то добавьте в разделе Марка ТС",
        related_name='marka'
    )
    number = models.CharField("Номер ТС", max_length=20, unique=True)
    sorka = models.CharField("Номер СОРКИ", max_length=20, blank=True, null=True)
    
    number_pr = models.CharField("Номер прицепа", max_length=20, blank=True, null=True)
    sorka_pr = models.CharField("Номер СОРКИ прицепа", max_length=20, blank=True, null=True)

    photo1 = models.ImageField("Фото ТС", upload_to='photos/drivers/', blank=True, null=True)
    photo2 = models.ImageField("Фото СОРКИ спереди", upload_to='photos/drivers/', blank=True, null=True)
    photo3 = models.ImageField("Фото СОРКИ сзади", upload_to='photos/drivers/', blank=True, null=True)
    photo4 = models.ImageField("Фото СОРКИ прицепа спереди", upload_to='photos/drivers/', blank=True, null=True)
    photo5 = models.ImageField("Фото СОРКИ прицепа сзади", upload_to='photos/drivers/', blank=True, null=True)


    def __str__(self):
        return self.number
    
    class Meta:
        verbose_name = "Транспортное средство"
        verbose_name_plural = "Транспортные средства"
