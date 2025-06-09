from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from .models import Podryad
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin
from car.models import Car
class PodryadResource(resources.ModelResource):
    # Пример кастомных полей (если есть ForeignKey)
    # organization = fields.Field(
    #     column_name='organization',
    #     attribute='organization',
    #     widget=ForeignKeyWidget(Organization, 'name')
    # )
    class Meta:
        model = Podryad

class CarInline(admin.TabularInline):
    model = Car  # промежуточная таблица ManyToMany
    extra = 0
    verbose_name = "Трансортное средство"
    verbose_name_plural = "Транспортные средства"

    readonly_fields = ('car_link',)
    fields = ('car_link',)
    def car_link(self, instance):
        if instance.car:
            url = reverse('admin:car_car_change', args=[instance.car.pk])
            return format_html('<a href="{}">{}</a>', url, instance.car.number)
        return "-asdasdas"
    car_link.short_description = "ТС"


class PodryadAdmin(ImportExportActionModelAdmin):

    resource_class = PodryadResource
    
    # Дополнительные настройки админки
    list_display = ('org_name', 'full_name', 'cars_count')  # Замените на ваши поля
    list_filter = ('org_name',)
    search_fields = ('org_name',)    
    inlines = [CarInline]
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Добавляем аннотацию с подсчётом связанных машин
        qs = qs.annotate(_cars_count=Count('cars', distinct=True))
        return qs

    def cars_count(self, obj):
        return obj._cars_count
    cars_count.short_description = 'Количество машин'
    cars_count.admin_order_field = '_cars_count'
    


admin.site.register(Podryad, PodryadAdmin)