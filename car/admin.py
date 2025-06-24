from django.contrib import admin # type: ignore
from django.db.models import Count # type: ignore
from django.urls import reverse # type: ignore
from django.utils.html import format_html # type: ignore
from import_export.admin import ImportExportActionModelAdmin # type: ignore
from import_export import resources, fields, widgets # type: ignore
from import_export.widgets import ForeignKeyWidget # type: ignore
from .models import Car, CarMarka, CarModel
from pod.models import Podryad
from vod.models import Driver

class DriverInline(admin.TabularInline):
    model = Car.drivers.through
    extra = 0
    verbose_name = "Водитель"
    verbose_name_plural = "Водители"
    readonly_fields = ('driver_link',)

    def driver_link(self, obj):
        url = reverse('admin:vod_driver_change', args=[obj.driver.pk])
        return format_html('<a href="{}" target="_blank">{}</a>', url, obj.driver.full_name)
    driver_link.short_description = "Карточка водителя"

class CarResourse(resources.ModelResource):
    organization = fields.Field(
        attribute='contractor',  # Поле в модели
        column_name='contractor',  # Название столбца в CSV
        widget=ForeignKeyWidget(Podryad, 'org_name'),
        default=1
    )
    model = fields.Field(
        attribute='model',  # Поле в модели
        column_name='model',  # Название столбца в CSV
        widget=ForeignKeyWidget(CarModel, 'name'),
    )
    marka = fields.Field(
        attribute='marka',  # Поле в модели
        column_name='marka',  # Название столбца в CSV
        widget=ForeignKeyWidget(CarMarka, 'name'),
    )
    is_active = fields.Field(
        attribute='is_approved',
        column_name='is_approved',
        widget=widgets.BooleanWidget()  # Специальный виджет для булевых значений
    )
    class Meta:
        model = Car

@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'cars_count')
    search_fields = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Добавляем аннотацию с подсчётом связанных машин
        qs = qs.annotate(_cars_count=Count('model', distinct=True))
        return qs

    def cars_count(self, obj):
        return obj._cars_count
    cars_count.short_description = 'Количество машин'
    cars_count.admin_order_field = '_cars_count'


@admin.register(CarMarka)
class CarMarkaAdmin(admin.ModelAdmin):
    list_display = ('name', 'cars_count')
    search_fields = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Добавляем аннотацию с подсчётом связанных машин
        qs = qs.annotate(_cars_count=Count('marka', distinct=True))
        return qs

    def cars_count(self, obj):
        return obj._cars_count
    cars_count.short_description = 'Количество машин'
    cars_count.admin_order_field = '_cars_count'
    
class DriverInline(admin.TabularInline):
    model = Driver.cars.through  # промежуточная таблица ManyToMany
    extra = 0
    verbose_name = "Водитель"
    verbose_name_plural = "Водители"
    readonly_fields = ('driver_link',)
    fields = ('driver_link',) 

    def driver_link(self, obj):
        # driver = instance.driver  # или instance.driver_id, зависит от модели
        if obj.driver:
            url = reverse('admin:vod_driver_change', args=[obj.driver.pk])
            return format_html('<a href="{}">{} {}</a>', url, obj.driver.full_name, obj.driver.birth_date)
        return "-"
    driver_link.short_description = "Водитель"
    # Можно добавить поля из Driver, если нужно

class CarAdmin(ImportExportActionModelAdmin):
    resource_class = CarResourse
    list_display = ("model",'contractor', "marka", "number", "drivers_count")
    list_filter = ("model", "marka",'contractor')
    search_fields = ("number","drivers__full_name")
    inlines = [DriverInline]
    # filter_horizontal = ("drivers",) if hasattr(Car, 'drivers') else () 

    def get_form(self, request, obj = ..., change = ..., **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['model'].widget.can_add_related = False # Фалсе запрещает добавить новый элемент сразу
        form.base_fields['marka'].widget.can_add_related = False
        return form
    
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(drivers_num=Count('drivers'))

    def drivers_count(self, obj):
        return obj.drivers_num
    drivers_count.short_description = 'Количество водителей'
    drivers_count.admin_order_field = 'drivers_num'


    
admin.site.register(Car, CarAdmin)