from django.contrib import admin # type: ignore
from django.db.models import Count, Q # type: ignore
from django.urls import reverse # type: ignore
from django.utils.html import format_html, escape # type: ignore
from .models import Podryad, PodryadPhoto # type: ignore
from car.models import Car
from vod.models import Driver
from import_export import resources, fields # type: ignore
from import_export.widgets import ForeignKeyWidget # type: ignore
from import_export.admin import ImportExportActionModelAdmin # type: ignore
from car.models import Car
from reestr.models import Registry

class PodryadResource(resources.ModelResource):
    class Meta:
        model = Podryad

class PodryadPhotoInline(admin.TabularInline):
    model = PodryadPhoto
    extra = 1 # Количество пустых форм для загрузки
    fields = ('image', 'description')
    verbose_name = "Фотография"
    verbose_name_plural = "Фотоальбом"
    
    classes = ('collapse',)
        
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
    
    classes = ('collapse',)
    # Метод для добавления прямой ссылки на полную запись в реестре
    def has_add_permission(self, request, obj=None):
        return False
    
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
    list_display = ('org_name', 'contract_number', 'user', 'drivers_count', 'cars_count')
    
    list_filter = ('org_name',)
    search_fields = ('org_name',"drivers__full_name", "cars__number", 'user__username')    
    inlines = [PodryadPhotoInline, RegistryInlineForPodryad]
    raw_id_fields = ('user',)
    filter_horizontal = ('drivers',)
    autocomplete_fields = ('cars',)
    readonly_fields = ('get_drivers_with_cars',)
    
    fieldsets = (
        ("Основная информация", {
            'fields': ('org_name', 'contract_number', 'user', 'full_name')
        }),
        ("Управление командой и парком", {'fields': ('drivers', 'cars')}),
        ("Список водителей и их ТС", {'classes': ('collapse',), 'fields': ('get_drivers_with_cars',)}),
        
        ("Контактные и банковские данные", {
            'classes': ('collapse',),
            'fields': ('email', 'phone_1', 'phone_2', 'phone_3', 'bank', 'inn', 'num_chet', 'num_bik', 'num_corch','kpp', 'ogrn', 'okpo')
        }),
        ("Паспортные данные и адреса", {
            'classes': ('collapse',),
            'fields': ('birth_date', 'snils', 'issued_by', 'issue_date', 'number', 'series', 'registration', 'adress')
        })
    )

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
        # Аннотируем для сортировки по количеству машин и водителей
        qs = qs.annotate(
            _cars_count=Count('cars', distinct=True),
            _drivers_count=Count('drivers', distinct=True)
        )
        return qs

    def cars_count(self, obj):
        return obj._cars_count
    cars_count.short_description = 'Кол-во машин'
    cars_count.admin_order_field = '_cars_count'

    def drivers_count(self, obj):
        return obj._drivers_count
    drivers_count.short_description = 'Кол-во водителей'
    drivers_count.admin_order_field = '_drivers_count'
    
    def get_drivers_with_cars(self, obj):
        """Формирует HTML-список водителей с их машинами и ссылками."""
        drivers = obj.drivers.prefetch_related('cars').all()
        if not drivers:
            return "К этому подрядчику еще не прикреплены водители."
            
        html = "<ul style='list-style-type: none; padding-left: 0;'>"
        for driver in drivers:
            # Получаем машины, привязанные к водителю
            cars_str = ", ".join([car.number for car in driver.cars.all()])
            if not cars_str:
                cars_str = "<i>(машина не закреплена)</i>"
            
            # Ссылка на карточку водителя
            driver_url = reverse('admin:vod_driver_change', args=[driver.pk])
            
            html += (f"<li style='margin-bottom: 8px;'>"
                    f"<strong><a href='{driver_url}'>{driver.full_name}</a></strong>"
                    f" &mdash; ТС: {cars_str}"
                    f"</li>")
        html += "</ul>"
        return format_html(html)
    get_drivers_with_cars.short_description = "Список водителей и их транспорт"