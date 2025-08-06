from django.contrib import admin # type: ignore
from django.db.models import Count, Q # type: ignore
from django.urls import reverse # type: ignore
from django.utils.html import format_html # type: ignore
from import_export.admin import ImportExportActionModelAdmin # type: ignore
from import_export import resources, fields, widgets # type: ignore
from import_export.widgets import ForeignKeyWidget # type: ignore
from .models import Car, CarMarka, CarModel
from pod.models import Podryad
from vod.models import Driver
from reestr.models import Registry

class DriverInline(admin.TabularInline):
    model = Driver
    fk_name = "cars"
    readonly_fields = ('driver_link',)
    fields = ('driver_link',)
    extra = 0
    verbose_name = "Закрепленный водитель"
    verbose_name_plural = "Закрепленные водители"

    def driver_link(self, obj):
        if obj.pk:
            url = reverse('admin:vod_driver_change', args=[obj.pk])
            return format_html('<a href="{}">{}</a>', url, obj.full_name)
        return "-"
    driver_link.short_description = "Водитель"

    # Запрещаем добавлять водителей со страницы машины
    def has_add_permission(self, request, obj=None):
        return False

    # Запрещаем удалять водителей со страницы машины
    def has_delete_permission(self, request, obj=None):
        return False

class RegistryInlineForCar(admin.TabularInline):
    model = Registry
    fk_name = 'number' # Поле в модели Registry, которое ссылается на Car
    
    # Поля, которые будут видны в инлайне
    fields = ('numberPL', 'dataPOPL', 'driver', 'pod', 'tonn', 'view_link')
    readonly_fields = fields # Делаем все поля только для чтения
    
    extra = 0 # Не показывать пустые формы для добавления
    can_delete = False # Запретить удаление отсюда
    verbose_name = "Рейс"
    verbose_name_plural = "История рейсов на этом ТС"

    def has_add_permission(self, request, obj=None):
        return False # Запретить добавление

    # Ссылка на полную запись в реестре
    def view_link(self, obj):
        if obj.pk:
            url = reverse('admin:reestr_registry_change', args=[obj.pk])
            return format_html('<a href="{}">Открыть рейс</a>', url)
        return ""
    view_link.short_description = "Ссылка"

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

@admin.register(Car)
class CarAdmin(ImportExportActionModelAdmin):
    resource_class = CarResourse
    list_display = ("model",'contractor', "marka", "number", "drivers_count")
    list_filter = ("model", "marka",'contractor')
    search_fields = ("number",)
    inlines = [DriverInline, RegistryInlineForCar]
    
    def get_search_results(self, request, queryset, search_term):
        _, use_distinct = super().get_search_results(request, queryset, search_term)

        if search_term:
            # Ищем по номеру машины без учета регистра
            queryset = queryset.filter(number__icontains=search_term)
        
        return queryset, use_distinct
    
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(drivers_num=Count('drivers'))

    def drivers_count(self, obj):
        return obj.drivers_num
    drivers_count.short_description = 'Количество водителей'
    drivers_count.admin_order_field = 'drivers_num'
