from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from .models import Registry, Marsh, Gruz
from car.models import Car #,CarMarka
from pod.models import Podryad
from vod.models import Driver
from import_export.instance_loaders import CachedInstanceLoader


class StrippedForeignKeyWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value or str(value).strip() == '':
            return None  # Возвращаем None для пустых значений
            
        value = str(value).strip().lower()
        
        # Ищем в базе без учета регистра и пробелов
        for obj in self.model.objects.all():
            field_val = getattr(obj, self.field)
            if field_val and field_val.strip().lower() == value:
                return obj
                
        # Если не найден - создаем нового водителя (опционально)
        # return self.model.objects.create(**{self.field: value.title()})
        
        raise self.model.DoesNotExist(
            f'Объект {self.model.__name__} с {self.field}={value} не найден'
        )
    
@admin.register(Marsh)
class MarshAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Gruz)
class GruzAdmin(admin.ModelAdmin):
    list_display = ("name",)

class RegistryResource(resources.ModelResource):
    instance_loader_class = CachedInstanceLoader

    driver = fields.Field(
        column_name='driver',        # имя столбца в файле
        attribute='driver',          # имя поля модели Registry
        widget=StrippedForeignKeyWidget(Driver, 'full_name')  # поле модели Driver для поиска
    )
    driver2 = fields.Field(
        column_name='driver2',
        attribute='driver2',
        widget=StrippedForeignKeyWidget(Driver, 'full_name')
    )
    pod = fields.Field(
        column_name='pod',
        attribute='pod',
        widget=StrippedForeignKeyWidget(Podryad, 'org_name')
    )
    number = fields.Field(
        column_name='number',
        attribute='number',
        widget=StrippedForeignKeyWidget(Car, 'number')
    )
    # marka = fields.Field(
    #     column_name='marka',
    #     attribute='marka',
    #     widget=StrippedForeignKeyWidget(CarMarka, 'name')
    # )
    marsh = fields.Field(
        column_name='marsh',
        attribute='marsh',
        widget=StrippedForeignKeyWidget(Marsh, 'name'),
    )

    gruz = fields.Field(
        column_name='gruz',
        attribute='gruz',
        widget=ForeignKeyWidget(Gruz, "id")
    )

    class Meta:
        model = Registry
        import_id_fields = ( 'numberPL', 'driver', 'driver2', 'pod', 'number', 'marsh')
        fields = (
            'driver', 'driver2', 'pod', 'number', 'marsh',
            'numberPL', 'dataPOPL', 'dataSDPL',
            'numberTN', 'dataPOG', 'dataVYG', 'gruz', 'tonn', 'gsm', 'gsmVY', 
            'gsmVO', 'gsmRS', 'comment', 'status'
        )
        skip_unchanged = True
        report_skipped = True
        use_bulk = True
        batch_size = 1000
        

@admin.register(Registry)
class RegistryAdmin(ImportExportModelAdmin):
    resource_class = RegistryResource
    list_display = ('numberPL', 'driver', 'driver2', 'pod', 'number', 'marsh', 'dataPOPL', 'tonn')
    search_fields = ('numberPL', 'driver__full_name', 'driver2__full_name', 'number__number')
    list_filter = ('gruz','pod', 'dataPOPL')
