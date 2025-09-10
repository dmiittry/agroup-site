from django.contrib import admin # type: ignore
from django.db.models import Count, Q # type: ignore
from import_export.admin import ImportExportModelAdmin # type: ignore
from django.utils.html import format_html, escape # type: ignore
from django.urls import reverse # type: ignore
from .models import Driver, DriverPhoto
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

class DriverPhotoInline(admin.TabularInline):
    model = DriverPhoto
    extra = 1
    fields = ('image', 'description')
    verbose_name = "Фотография"
    verbose_name_plural = "Фотоальбом водителя"

class DriverResource(resources.ModelResource):
    cars = fields.Field(
        attribute='cars',
        column_name='cars',
        widget=ManyToManyWidget(Car, field='number'),
    )
    is_approved = fields.Field(
        attribute='is_approved', widget=BooleanWidget()
    )
    class Meta:
        model = Driver

class ReadOnlyRegistryInline(admin.TabularInline):
    model = Registry
    fields = ('numberPL', 'dataPOPL', 'number', 'marsh', 'tonn', 'status', 'view_link')
    readonly_fields = fields
    can_delete = False
    extra = 0
    classes = ('collapse',)
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

@admin.register(Driver)
class DriverModelAdmin(ImportExportModelAdmin):
    resource_class = DriverResource
    list_display = (
        "full_name", 'user', 'display_cars', 'display_contractors',
        "solo_trips", "joint_trips", "is_approved", "dopog"
    )
    search_fields = (
        "full_name", "phone_1", 'user__username',
        'cars__number', 'contractors__org_name', "dopog" # Обновлено для M2M
    )
    list_filter = (MarshFilter, SeasonFilter, 'is_approved') # Убран 'contractor'
    raw_id_fields = ('user',)
    inlines = [
        DriverPhotoInline, # Добавлен фотоальбом
        SoloRegistryInline, JointRegistryInline, JointRegistry2Inline
    ]
    # Улучшенный интерфейс для выбора нескольких машин
    filter_horizontal = ('cars',) 
    # УЛУЧШЕНИЕ: Добавляем новое поле и статистику в readonly
    readonly_fields = ('display_contractors_list', 'contractors_stats', 'cars_stats')

    # УЛУЧШЕНИЕ: Группируем поля для удобства
    fieldsets = (
        ("Статус и доступ", {"fields": ('user', 'is_approved', 'can_login')}),
        ("Основная информация", {"fields": ('full_name', 'driver_license', 'vy_date', 'snils', 'phone_1' )}),
        ("Привязки и статистика", {"fields": ('cars', 'display_contractors_list', 'contractors_stats', 'cars_stats')}),
        ("Документы", {"classes": ('collapse',), "fields": ('dopog','birth_date', 'issued_by', 'issue_date', 'number', 'series', 'registration','phone_2', 'phone_3')})
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('cars', 'contractors').annotate(
            solo_trips_count=Count('primary_registries', filter=Q(primary_registries__driver2__isnull=True), distinct=True),
            joint_trips_count_primary=Count('primary_registries', filter=Q(primary_registries__driver2__isnull=False), distinct=True),
            joint_trips_count_secondary=Count('secondary_registries', distinct=True)
        )

    def display_cars(self, obj):
        cars = obj.cars.all()
        if not cars:
            return "Не закреплена"
        
        html_list = [
            f'<a href="{reverse("admin:car_car_change", args=(c.pk,))}">{escape(c.number)}</a>'
            for c in cars
        ]
        return format_html(", ".join(html_list))
    display_cars.short_description = 'Закрепленные ТС'

    def display_contractors(self, obj):
        html_list = [f'<a href="{reverse("admin:pod_podryad_change", args=(c.pk,))}">{escape(c.org_name)}</a>' for c in obj.contractors.all()]
        return format_html(", ".join(html_list)) if html_list else "Не привязан"
    display_contractors.short_description = 'Подрядчики'

    # --- УЛУЧШЕНИЕ: Новый метод для отображения подрядчиков внутри карточки ---
    def display_contractors_list(self, obj):
        contractors = obj.contractors.all()
        if not contractors: return "Водитель не привязан ни к одному подрядчику."
        html = "".join([f"<li><a href='{reverse('admin:pod_podryad_change', args=[c.pk])}'>{escape(c.org_name)}</a></li>" for c in contractors])
        return format_html("<ul style='list-style-type: none; padding-left: 0;'>{}</ul>", format_html(html))
    display_contractors_list.short_description = "Привязан к подрядчикам"
    
    # --- Статистика (без изменений) ---
    def contractors_stats(self, obj):
        stats = Registry.objects.filter(Q(driver=obj) | Q(driver2=obj)).values('pod__org_name').annotate(cnt=Count('id')).order_by('-cnt')
        return format_html("<br>".join([f"{row['pod__org_name']}: {row['cnt']}" for row in stats])) if stats else "Нет данных"
    contractors_stats.short_description = "Рейсы по подрядчикам"

    def cars_stats(self, obj):
        stats = Registry.objects.filter(Q(driver=obj) | Q(driver2=obj)).values('number__number').annotate(cnt=Count('id')).order_by('-cnt')
        return format_html("<br>".join([f"{row['number__number']}: {row['cnt']}" for row in stats])) if stats else "Нет данных"
    cars_stats.short_description = "Рейсы по машинам"

    def solo_trips(self, obj):
        return obj.solo_trips_count
    solo_trips.short_description = 'Одиночные рейсы'

    def joint_trips(self, obj):
        return obj.joint_trips_count_primary + obj.joint_trips_count_secondary
    joint_trips.short_description = 'Совместные рейсы'

    def get_inline_instances(self, request, obj=None):
        inline_instances = []
        for inline_class in self.inlines:
            inline = inline_class(self.model, self.admin_site)
            # Эта строка передает родительский объект в инлайн, что нужно для ваших фильтров
            inline.parent_object = obj 
            inline_instances.append(inline)
        return inline_instances
    