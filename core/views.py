from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Visitor, LocationLog
from datetime import datetime
import pytz
from django.utils import timezone
import json
from django.views.decorators.csrf import csrf_exempt

def home(request):
    return render(request, 'core/home.html')

@login_required
def register_visitor(request):
    if request.method == "POST":
        nat_type = request.POST.get('nationality')
        Visitor.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            age=request.POST.get('age'),
            nationality_type=nat_type,
            national_id=request.POST.get('national_id') if nat_type == 'thai' else None,
            passport_number=request.POST.get('passport_number') if nat_type == 'foreigner' else None,
            
            contact_number=request.POST.get('contact_number'), 
            
            device_code=request.POST.get('device_code'),
            is_active=True
        )
        return redirect('core:dashboard')
    return render(request, 'core/register.html')

@login_required
def dashboard(request):
    query = request.GET.get('q', '')
    visitor = None
    route_data = []

    if query:
        visitors = Visitor.objects.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(device_code__icontains=query)
        ).order_by('-registered_at')
        
        if visitors.exists():
            visitor = visitors.first()
            
            # 🚨 [ปลดล็อคแล้ว] ดึงพิกัดทั้งหมดของรหัสอุปกรณ์นี้มาโชว์เลย ไม่สนใจเวลาลงทะเบียน
            logs = LocationLog.objects.filter(
                device_code=visitor.device_code
            )
            
            # ถ้าคืนอุปกรณ์แล้ว ให้ตัดจบเส้นทางแค่เวลาที่คืน (ถ้ามี)
            if not visitor.is_active and hasattr(visitor, 'returned_at') and visitor.returned_at:
                logs = logs.filter(timestamp__lte=visitor.returned_at)
                
            logs = logs.order_by('timestamp')
            
            route_data = [[log.latitude, log.longitude, log.timestamp.isoformat()] for log in logs]

    return render(request, 'core/dashboard.html', {
        'visitor': visitor,
        'route_json': json.dumps(route_data),
        'query': query
    })

@login_required
def return_device(request, visitor_id):
    visitor = Visitor.objects.get(id=visitor_id)
    visitor.is_active = False
    
    if hasattr(visitor, 'returned_at'):
        visitor.returned_at = timezone.now()
        
    visitor.save()
    return redirect('core:dashboard')

@csrf_exempt
def api_upload_log(request):
    device_code = request.GET.get('device_code')

    if not device_code:
        return JsonResponse({'status': 'error', 'msg': 'Missing device_code'}, status=400)

    if request.method == 'POST':
        raw_body = request.body.decode('utf-8', errors='ignore')
        
        print("\n========== 📥 DATA FROM ARDUINO ==========")
        print(raw_body)
        print("==========================================\n")

        lines = raw_body.split('\n')
        success_count = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue 
            
            try:
                clean_data = line.replace(" ", "").replace("%20", "")
                parts = clean_data.split(',')
                
                if len(parts) >= 4:
                    lat = float(parts[0])
                    lng = float(parts[1])
                    date_raw = parts[2]
                    time_raw = parts[3]
                    
                    try:
                        date_str = str(date_raw).zfill(6)
                        time_str = str(time_raw).zfill(8)
                        
                        d = int(date_str[0:2])
                        m = int(date_str[2:4])
                        y = int(date_str[4:6]) + 2000
                        H = int(time_str[0:2])
                        M = int(time_str[2:4])
                        S = int(time_str[4:6])
                        
                        dt_utc = datetime(y, m, d, H, M, S, tzinfo=pytz.utc)
                        dt_aware = dt_utc.astimezone(pytz.timezone('Asia/Bangkok'))
                        
                    except Exception as time_e:
                        print(f"⚠️ แปลงเวลาผิดพลาด: {time_e}")
                        dt_aware = timezone.now()

                    LocationLog.objects.create(
                        device_code=device_code,
                        latitude=lat,
                        longitude=lng,
                        timestamp=dt_aware
                    )
                    success_count += 1
                else:
                    print(f"⚠️ ข้อมูลไม่ครบ 4 ส่วน: '{line}'")
                    
            except Exception as e:
                print(f"❌ ERROR เซฟไม่ได้ บรรทัด '{line}' -> สาเหตุ: {e}")
                continue 

        print(f"✅ สรุป: บันทึกสำเร็จทั้งหมด {success_count} แถว\n")
        return JsonResponse({'status': 'success', 'msg': f'Saved {success_count} records'})

    return JsonResponse({'status': 'error', 'msg': 'Invalid request method'}, status=400)