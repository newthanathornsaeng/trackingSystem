from django.contrib import admin
from .models import Visitor, LocationLog

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    # ✅ ใช้ contact_number แทน
    list_display = ('first_name', 'last_name', 'nationality_type', 'contact_number', 'device_code', 'is_active')
    search_fields = ('first_name', 'last_name', 'device_code', 'national_id', 'passport_number', 'contact_number')
    list_filter = ('is_active', 'nationality_type', 'registered_at')

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser 

@admin.register(LocationLog)
class LocationLogAdmin(admin.ModelAdmin):
    list_display = ('device_code', 'latitude', 'longitude', 'timestamp')
    search_fields = ('device_code',)
    list_filter = ('timestamp', 'device_code')

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser