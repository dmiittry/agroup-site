from django.db import models

class Season(models.Model):
    name = models.CharField("Название сезона", max_length=100, unique=True)
    date_start = models.DateField("Дата начала", blank=True, null=True, db_index=True)
    date_end = models.DateField("Дата окончания", blank=True, null=True, db_index=True)
    is_active = models.BooleanField("Активен", default=True, db_index=True)
    description = models.TextField("Комментарий", blank=True, null=True)

    class Meta:
        verbose_name = "Сезон"
        verbose_name_plural = "Сезоны"
        ordering = ['-date_start', 'name']

    def __str__(self):
        return self.name