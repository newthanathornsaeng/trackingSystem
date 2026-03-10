from django.db import models

class Visitor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    nationality_type = models.CharField(max_length=20) # 'thai' หรือ 'foreigner'
    
    national_id = models.CharField(max_length=13, null=True, blank=True)
    passport_number = models.CharField(max_length=20, null=True, blank=True)
    
    device_code = models.CharField(max_length=50, db_index=True)
    is_active = models.BooleanField(default=True) # True=ยืมอยู่, False=คืนแล้ว
    registered_at = models.DateTimeField(auto_now_add=True)
    
    # 🚨 สิ่งที่เพิ่มเข้ามา: ใช้ตีกรอบเวลา "สิ้นสุดทริป"
    returned_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} ({self.device_code})"

class LocationLog(models.Model):
    device_code = models.CharField(max_length=50, db_index=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.device_code} - {self.timestamp}"