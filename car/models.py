from django.db import models # type: ignore

class CarPhoto(models.Model):
    car = models.ForeignKey(
        'Car',
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name="Транспортное средство"
    )
    image = models.ImageField("Фото", upload_to='photos/car_album/')
    description = models.CharField("Краткое описание", max_length=255, blank=True)

    class Meta:
        verbose_name = "Фотография ТС"
        verbose_name_plural = "Фотографии ТС"
        
    def __str__(self):
        return f"Фото для {self.car.number}"
    
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

    model = models.ForeignKey(
        CarModel,
        on_delete=models.CASCADE,
        verbose_name="Вид ТС",
        help_text="Если нету в списке, то добавьте в разделе Вид ТС",
        related_name='cars_by_model'
    )
    marka = models.ForeignKey(
        CarMarka,
        on_delete=models.CASCADE,
        verbose_name="Марка ТС",
        help_text="Если нету в списке, то добавьте в разделе Марка ТС",
        related_name='cars_by_marka'
    )
    number = models.CharField("Номер ТС", max_length=20, unique=True)
    sorka = models.CharField("Номер СОРКИ", max_length=20, blank=True, null=True)
    
    number_pr = models.CharField("Номер прицепа", max_length=20, blank=True, null=True)
    sorka_pr = models.CharField("Номер СОРКИ прицепа", max_length=20, blank=True, null=True)

    def __str__(self):
        return self.number
    
    class Meta:
        verbose_name = "Транспортное средство"
        verbose_name_plural = "Транспортные средства"
        ordering = ['number']