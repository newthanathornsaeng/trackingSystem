from django.contrib import admin
from .models import Visitor, LocationLog

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'nationality_type', 'device_code', 'is_active', 'registered_at')
    search_fields = ('first_name', 'last_name', 'device_code', 'national_id', 'passport_number')
    list_filter = ('is_active', 'nationality_type', 'registered_at')

    # ✅ เพิ่มฟังก์ชันนี้เพื่อล็อคสิทธิ์การลบ
    def has_delete_permission(self, request, obj=None):
        # ถ้าเป็น Superuser (Admin) จะ return True (ลบได้)
        # ถ้าไม่ใช่ จะ return False (ปุ่มลบจะหายไป)
        return request.user.is_superuser 

@admin.register(LocationLog)
class LocationLogAdmin(admin.ModelAdmin):
    list_display = ('device_code', 'latitude', 'longitude', 'timestamp')
    search_fields = ('device_code',)
    list_filter = ('timestamp',)

    # ✅ ล็อคไม่ให้ลบข้อมูลพิกัดด้วยเช่นกัน
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser