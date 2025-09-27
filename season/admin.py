from django.contrib import admin
from .models import Season

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_start', 'date_end', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)