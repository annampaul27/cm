from django.contrib import admin
from .models import MaintenanceRequest


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'priority', 'status', 'location', 'date_reported')
    list_filter = ('category', 'priority', 'status')
    search_fields = ('title', 'description', 'location')
