from django.contrib import admin
from django.db.models import Count
from import_export.admin import ImportExportModelAdmin
from .models import Driver
from car.models import Car
from import_export import resources, fields
from import_export.widgets import ManyToManyWidget, BooleanWidget

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



class DriverModelAdmin(ImportExportModelAdmin):
    resource_class = DriverResource
    list_display = ("full_name", 'cars_count', "birth_date", "phone_1", "driver_license", "snils", "is_approved")
    search_fields = ("full_name", "phone_1", "is_approved")
    filter_horizontal = ("cars",)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Добавляем аннотацию с подсчётом связанных машин
        qs = qs.annotate(_cars_count=Count('cars', distinct=True))
        return qs

    def cars_count(self, obj):
        return obj._cars_count
    cars_count.short_description = 'Количество машин'
    cars_count.admin_order_field = '_cars_count'

admin.site.register(Driver, DriverModelAdmin)