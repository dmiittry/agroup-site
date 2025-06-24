from django.contrib import admin # type: ignore
from django.db.models import Count # type: ignore
from django.urls import reverse # type: ignore
from django.utils.html import format_html # type: ignore
from .models import Podryad # type: ignore
from car.models import Car
from vod.models import Driver
from import_export import resources, fields # type: ignore
from import_export.widgets import ForeignKeyWidget # type: ignore
from import_export.admin import ImportExportActionModelAdmin # type: ignore
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
    model = Car
    extra = 0
    fields = ('number', 'car_link', 'drivers_list')
    readonly_fields = ('car_link', 'drivers_list')

    def car_link(self, obj):
        url = reverse('admin:car_car_change', args=[obj.pk])
        return format_html('<a href="{}" target="_blank">{}</a>', url, obj.number)
    car_link.short_description = "Карточка ТС"

    def drivers_list(self, obj):
        # Исправлено: получаем водителей через обратную связь
        drivers = Driver.objects.filter(cars=obj)
        return ", ".join([f"{d.full_name}" for d in drivers])
    drivers_list.short_description = "Водители"

class DriverInline(admin.TabularInline):
    model = Driver
    extra = 0
    fields = ('full_name', 'driver_link')
    readonly_fields = ('driver_link',)

    def driver_link(self, obj):
        url = reverse('admin:vod_driver_change', args=[obj.pk])
        return format_html('<a href="{}" target="_blank">{}</a>', url, obj.full_name)
    driver_link.short_description = "Карточка водителя"


class PodryadAdmin(ImportExportActionModelAdmin):

    resource_class = PodryadResource
    
    # Дополнительные настройки админки
    list_display = ('org_name', 'full_name', 'cars_count')  # Замените на ваши поля
    list_filter = ('org_name',)
    search_fields = ('org_name',"drivers", "cars")    
    inlines = [CarInline, DriverInline]
    # filter_horizontal = ("drivers", "cars")
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