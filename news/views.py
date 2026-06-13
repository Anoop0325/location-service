import json
# pyrefly: ignore [missing-import]
from django.shortcuts import render
# pyrefly: ignore [missing-import]
from django.http import JsonResponse
# pyrefly: ignore [missing-import]
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import UserLocation

@ensure_csrf_cookie
def news_detail(request):
    return render(request, 'news/news_detail.html')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def save_location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lat = data.get('latitude')
            lng = data.get('longitude')
            accuracy = data.get('accuracy')
            
            if lat is not None and lng is not None:
                location = UserLocation.objects.create(
                    latitude=lat,
                    longitude=lng,
                    accuracy=accuracy,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                return JsonResponse({'status': 'success', 'id': location.id})
            return JsonResponse({'status': 'error', 'message': 'Missing coordinates'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed'}, status=405)
