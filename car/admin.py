# car/admin.py

from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html, escape
from import_export.admin import ImportExportActionModelAdmin # type: ignore
from import_export import resources # type: ignore

from .models import Car, CarMarka, CarModel, CarPhoto
from reestr.models import Registry

class CarPhotoInline(admin.TabularInline):
    model = CarPhoto; extra = 1; fields = ('image', 'description'); verbose_name = "Фотография"; verbose_name_plural = "Фотоальбом ТС"

class RegistryInlineForCar(admin.TabularInline):
    model = Registry; fk_name = 'number'; fields = ('numberPL', 'dataPOPL', 'driver', 'pod', 'tonn', 'status', 'view_link'); 
    readonly_fields = fields; extra = 0; 
    can_delete = False; verbose_name = "Рейс"; 
    verbose_name_plural = "История рейсов на этом ТС"; 
    classes = ('collapse',)
    
    def has_add_permission(self, request, obj=None):
        return False
    def view_link(self, obj):
        if obj.pk: 
            return format_html('<a href="{}">Открыть рейс</a>', reverse('admin:reestr_registry_change', args=[obj.pk]))
        return ""
    view_link.short_description = "Ссылка"

class CarResource(resources.ModelResource):
    class Meta: model = Car

@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'cars_count'); search_fields = ('name',)
    def get_queryset(self, request): 
        return super().get_queryset(request).annotate(_cars_count=Count('cars_by_model'))
    def cars_count(self, obj): 
        return obj._cars_count
    cars_count.short_description = 'Количество машин'

@admin.register(CarMarka)
class CarMarkaAdmin(admin.ModelAdmin):
    list_display = ('name', 'cars_count'); search_fields = ('name',)
    def get_queryset(self, request): 
        return super().get_queryset(request).annotate(_cars_count=Count('cars_by_marka'))
    def cars_count(self, obj): 
        return obj._cars_count
    cars_count.short_description = 'Количество машин'

@admin.register(Car)
class CarAdmin(ImportExportActionModelAdmin):
    resource_class = CarResource
    list_display = ("number", "model", "marka", "contractors_list", )
    search_fields = ("number", "podryads__org_name")  # поиск ТС по названию подрядчика
    list_filter = ("model", "marka",) 
    
    inlines = [CarPhotoInline, RegistryInlineForCar]
    
    readonly_fields = ('contractors_list','display_drivers_list',)
    
    fieldsets = (
        ("Основная информация", {'fields': ('number', 'model', 'marka')}),
        ("Закрепленные водители", {'fields': ('display_drivers_list',)}),
        ("Документы на ТС", {'classes': ('collapse',), 'fields': ('sorka', 'number_pr', 'sorka_pr')}),
    )
    
    def contractors_list(self, obj):
        names = [p.org_name for p in obj.podryads.all()]
        return ", ".join(names) if names else "Не закреплен"
    contractors_list.short_description = "Подрядчики"
    
    def get_queryset(self, request): 
        return super().get_queryset(request).prefetch_related('drivers')
    
    def display_drivers(self, obj): 
        return ", ".join([d.full_name for d in obj.drivers.all()]) or "Не закреплен"
    display_drivers.short_description = 'Водители'

    def display_drivers_list(self, obj):
        drivers = obj.drivers.all()
        if not drivers: 
            return "За машиной не закреплен ни один водитель."
        items = []
        for d in drivers:
            url = reverse('admin:vod_driver_change', args=[d.pk])
            items.append(f'<li><a href="{url}">{escape(d.full_name)}</a></li>')
        return format_html('<ul>{}</ul>', format_html("".join(items)))
        # html = "".join([f"<li><a href='{reverse('admin:vod_driver_change', args=[d.pk])}'>{escape(d.full_name)}</a></li>" for d in drivers])
        # return format_html("<ul style='padding-left:0;'>{}</ul>", format_html(html))
    
    display_drivers_list.short_description = "Список водителей"
    
    def display_owners(self, obj):
        owners = obj.owners.all()
        if not owners:
            return "Без владельца"
        return ", ".join([owner.org_name for owner in owners])
    display_owners.short_description = "Владельцы (Подрядчики)"
