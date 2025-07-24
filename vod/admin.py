from django.contrib import admin # type: ignore
from django.db.models import Count, Q # type: ignore
from import_export.admin import ImportExportModelAdmin # type: ignore
from django.utils.html import format_html # type: ignore
from django.urls import reverse # type: ignore
from .models import Driver
from car.models import Car
from reestr.models import Registry, Marsh
from import_export import resources, fields # type: ignore
from import_export.widgets import ManyToManyWidget, BooleanWidget # type: ignore
from datetime import date

class MarshFilter(admin.SimpleListFilter):
    title = 'Маршрут'
    parameter_name = 'marsh'

    def lookups(self, request, model_admin):
        # Получаем только маршруты, по которым есть рейсы у водителей
        marsh_ids = Registry.objects.values_list('marsh', flat=True).distinct()
        return [(m.id, m.name) for m in Marsh.objects.filter(id__in=marsh_ids)]

    def queryset(self, request, queryset):
        if self.value():
            # Оставляем только водителей, у которых есть рейсы по выбранному маршруту
            return queryset.filter(
                primary_registries__marsh__id=self.value()
            ).distinct()
        return queryset
    
class SeasonFilter(admin.SimpleListFilter):
    title = 'Сезон'
    parameter_name = 'season'

    def lookups(self, request, model_admin):
        return [
            ('first', 'Зимник 2025 (01.12.24–01.04.25)'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'first':
            season_start = date(2024, 12, 1)
            season_end = date(2025, 5, 1)
            return queryset.filter(
                primary_registries__dataPOPL__gte=season_start,
                primary_registries__dataPOPL__lte=season_end
            ).distinct()
        return queryset
    
class NullableManyToManyWidget(ManyToManyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return []  # Возвращаем пустой список, чтобы очистить связи
        return super().clean(value, row, *args, **kwargs)
    
class DriverResource(resources.ModelResource):
    cars = fields.Field(
        attribute='cars',  # Поле в модели
        column_name='cars',  # Название столбца в CSV
        widget=NullableManyToManyWidget(Car, field='id', separator=','),
    )
    is_approved = fields.Field(
        column_name='is_approved',
        attribute='is_approved',
        widget=BooleanWidget(),
    )
    class Meta:
        model = Driver

class ReadOnlyRegistryInline(admin.TabularInline):
    model = Registry
    fields = ('numberPL', 'dataPOPL', 'number', 'marsh', 'tonn', 'status', 'view_link')
    readonly_fields = fields
    can_delete = False
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def view_link(self, obj):
        if obj.pk:
            url = reverse('admin:reestr_registry_change', args=[obj.pk])
            return format_html('<a href="{}" target="_blank">Открыть</a>', url)
        return ""
    view_link.short_description = "Реестр"
    
class SoloRegistryInline(ReadOnlyRegistryInline):
    fk_name = "driver"
    verbose_name = "Одиночный рейс"
    verbose_name_plural = "Одиночные рейсы"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(self, "parent_object") and self.parent_object:
            return qs.filter(driver = self.parent_object, driver2__isnull=True)
        return qs.none()

class JointRegistryInline(ReadOnlyRegistryInline):
    # Для совместных рейсов нужно два инлайна: по driver и по driver2.
    # Но если нужен один, используем fk_name='driver' и фильтруем по driver2__isnull=False и driver=self.parent_object,
    # а второй inline делаем по fk_name='driver2' и driver2=self.parent_object
    fk_name = 'driver'
    verbose_name = "Совместный рейс (как первый)"
    verbose_name_plural = "Совместные рейсы (как первый)"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(self, 'parent_object') and self.parent_object:
            return qs.filter(driver=self.parent_object, driver2__isnull=False)
        return qs.none()

class JointRegistry2Inline(ReadOnlyRegistryInline):
    fk_name = 'driver2'
    verbose_name = "Совместный рейс (как второй)"
    verbose_name_plural = "Совместные рейсы (как второй)"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(self, 'parent_object') and self.parent_object:
            return qs.filter(driver2=self.parent_object)
        return qs.none()

class CarInline(admin.TabularInline):
    model = Driver.cars.through
    extra = 0
    verbose_name = "Машина"
    verbose_name_plural = "Машины"
    readonly_fields = ('car_link',)

    def delete_model(self, request, obj):
        # Вместо удаления — просто отвязываем от подрядчика
        obj.car.pk = None
        obj.save()

    def car_link(self, obj):
        url = reverse('admin:car_car_change', args=[obj.car.pk])
        return format_html('<a href="{}" target="_blank">{}</a>', url, obj.car.number)
    car_link.short_description = "Карточка ТС"

class DriverModelAdmin(ImportExportModelAdmin):
    resource_class = DriverResource
    list_display = ("full_name", 'user', 'contractor', "solo_trips", "joint_trips", 'cars_count', "birth_date", "phone_1", "driver_license", "snils", "is_approved")
    search_fields = ("full_name", "phone_1", 'contractor__org_name', 'user__username')
    list_filter = (MarshFilter, SeasonFilter,  'is_approved', 'contractor')
    raw_id_fields = ('user',)
    inlines = [CarInline,SoloRegistryInline, JointRegistryInline, JointRegistry2Inline]
    filter_horizontal = ("cars",)
    readonly_fields = ('contractors_stats', 'cars_stats')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            _cars_count=Count('cars', distinct=True),
            solo_trips_count=Count(
                'primary_registries',
                filter=Q(primary_registries__driver2__isnull=True),
                distinct=True
            ),
            joint_trips_count_primary=Count(
                'primary_registries',
                filter=Q(primary_registries__driver2__isnull=False),
                distinct=True
            ),
            joint_trips_count_secondary=Count(
                'secondary_registries',
                distinct=True
            )
        )
        return qs
    
    def contractors_stats(self, obj):
        qs = Registry.objects.filter(Q(driver=obj) | Q(driver2=obj))
        stats = (
            qs.values('pod__org_name')
              .annotate(cnt=Count('id'))
              .order_by('-cnt')
        )
        if not stats:
            return "Нет данных"
        return format_html(
            "<br>".join(
                f"<b>{row['pod__org_name']}</b>: {row['cnt']}" for row in stats
            )
        )
    contractors_stats.short_description = "Рейсы по подрядчикам"

    def cars_stats(self, obj):
        qs = Registry.objects.filter(Q(driver=obj) | Q(driver2=obj))
        stats = (
            qs.values('number__number')
              .annotate(cnt=Count('id'))
              .order_by('-cnt')
        )
        if not stats:
            return "Нет данных"
        return format_html(
            "<br>".join(
                f"<b>{row['number__number']}</b>: {row['cnt']}" for row in stats
            )
        )
    cars_stats.short_description = "Рейсы по машинам"

    def cars_count(self, obj):
        return obj._cars_count
    cars_count.short_description = 'Количество машин'
    cars_count.admin_order_field = '_cars_count'

    def solo_trips(self, obj):
        return obj.solo_trips_count
    solo_trips.short_description = 'Одиночные рейсы'
    solo_trips.admin_order_field = 'solo_trips_count'

    def joint_trips(self, obj):
        return obj.joint_trips_count_primary + obj.joint_trips_count_secondary
    joint_trips.short_description = 'Совместные рейсы'
    joint_trips.admin_order_field = 'joint_trips_count_primary'

    def get_inline_instances(self, request, obj=None):
        inline_instances = []
        for inline_class in self.inlines:
            inline = inline_class(self.model, self.admin_site)
            inline.parent_object = obj
            inline_instances.append(inline)
        return inline_instances
    
admin.site.register(Driver, DriverModelAdmin)