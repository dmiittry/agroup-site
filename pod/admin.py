from django.contrib import admin # type: ignore
from django.db.models import Count, Q # type: ignore
from django.urls import reverse # type: ignore
from django.utils.html import format_html # type: ignore
from .models import Podryad # type: ignore
from car.models import Car
from vod.models import Driver
from import_export import resources, fields # type: ignore
from import_export.widgets import ForeignKeyWidget # type: ignore
from import_export.admin import ImportExportActionModelAdmin # type: ignore
from car.models import Car
from reestr.models import Registry

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

class RegistryInlineForPodryad(admin.TabularInline):
    model = Registry
    fk_name = 'pod' # Поле в модели Registry, которое ссылается на Podryad
    
    # Поля, которые мы хотим видеть в таблице
    fields = ('numberPL', 'dataPOPL', 'driver', 'number', 'tonn', 'status', 'view_link')
    readonly_fields = fields # Делаем все поля только для чтения
    
    extra = 0 # Не показывать пустые формы для добавления
    can_delete = False # Запретить удаление отсюда
    verbose_name = "Рейс"
    verbose_name_plural = "История рейсов подрядчика"

    def has_add_permission(self, request, obj=None):
        return False # Запретить добавление рейсов отсюда

    # Метод для добавления прямой ссылки на полную запись в реестре
    def view_link(self, obj):
        if obj.pk:
            url = reverse('admin:reestr_registry_change', args=[obj.pk])
            return format_html('<a href="{}">Открыть рейс</a>', url)
        return ""
    view_link.short_description = "Ссылка на рейс"
    
@admin.register(Podryad)
class PodryadAdmin(ImportExportActionModelAdmin):

    resource_class = PodryadResource
    
    # Дополнительные настройки админки
    list_display = ('org_name', 'user', 'full_name', 'cars_count')  # Замените на ваши поля
    list_filter = ('org_name',)
    search_fields = ('org_name',"drivers__full_name", "cars__number", 'user__username')    
    inlines = [CarInline, DriverInline, RegistryInlineForPodryad]
    raw_id_fields = ('user',)
    
    def get_search_results(self, request, queryset, search_term):
        # Вызываем родительский метод, чтобы получить use_distinct.
        # Сам queryset мы будем фильтровать по-своему.
        _, use_distinct = super().get_search_results(request, queryset, search_term)

        if search_term:
            # Создаем регистронезависимый поисковый запрос по нужным полям
            search_query = (
                Q(org_name__icontains=search_term) |
                Q(full_name__icontains=search_term) |
                Q(inn__icontains=search_term)
            )
            queryset = queryset.filter(search_query)

        return queryset, use_distinct
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Добавляем аннотацию с подсчётом связанных машин
        qs = qs.annotate(_cars_count=Count('cars', distinct=True))
        return qs

    def cars_count(self, obj):
        return obj._cars_count
    cars_count.short_description = 'Количество машин'
    cars_count.admin_order_field = '_cars_count'
