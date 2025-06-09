from django.db import models
from car.models import Car #, CarMarka
from pod.models import Podryad
from vod.models import Driver

class Gruz(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Вид груза"
        verbose_name_plural = "Виды груза"


class Marsh(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"

class Registry(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='primary_registries', verbose_name='Водитель')
    driver2 = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='secondary_registries', blank=True, null=True, verbose_name='Второй водитель')
    pod = models.ForeignKey(Podryad, on_delete=models.CASCADE, related_name="pod_reestr", verbose_name='Подрядчик')
    # marka = models.ForeignKey(CarMarka, on_delete=models.CASCADE, blank=True, null=True)
    number = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="carnumber_reestr", verbose_name='Номер ТС')
    marsh = models.ForeignKey(Marsh, on_delete=models.CASCADE, related_name="marsh_reestr", verbose_name='Маршрут')
    
    numberPL = models.CharField("Номер ПЛ", max_length=100, blank=True, null=True)
    dataPOPL = models.DateField("Дата погрузки", blank=True, null=True)
    # timePOPL = models.TimeField("Время погрузки", blank=True, null=True)
    # timeSDPL = models.TimeField("Время сдачи путевого листа", blank=True, null=True)
    dataSDPL = models.DateField("Дата сдачи путевого листа", blank=True, null=True)
    numberTN = models.CharField("Номер ТТН", max_length=100, blank=True, null=True)
    dataPOG = models.DateField("Дата погрузки груза", blank=True, null=True)
    dataVYG = models.DateField("Дата выгрузки груза", blank=True, null=True)
    tonn = models.DecimalField("Количество тонн", max_digits=10, decimal_places=2, blank=True, null=True)
    gruz = models.ForeignKey(Gruz, on_delete=models.CASCADE, related_name="gruz_reestr", blank=True, null=True, verbose_name='Вид груза')
    gsm = models.DecimalField("ГСМ", max_digits=10, decimal_places=2, blank=True, null=True)
    gsmVY = models.DecimalField("ГСМ ВЫ", max_digits=10, decimal_places=2, blank=True, null=True)
    gsmVO = models.DecimalField("ГСМ ВО", max_digits=10, decimal_places=2, blank=True, null=True)
    gsmRS = models.DecimalField("ГСМ РС", max_digits=10, decimal_places=2, blank=True, null=True)
    comment = models.TextField("Примечание",blank=True, null=True)
    status = models.CharField("Статус",max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Путевой лист {self.numberPL} - {self.driver.full_name}"

    class Meta:
        verbose_name = "Реестр"
        verbose_name_plural = "Реестры"
