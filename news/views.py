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
            session_id = data.get('session_id')
            
            if lat is not None and lng is not None:
                location = UserLocation.objects.create(
                    latitude=lat,
                    longitude=lng,
                    accuracy=accuracy,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    session_id=session_id
                )
                return JsonResponse({'status': 'success', 'id': location.id})
            return JsonResponse({'status': 'error', 'message': 'Missing coordinates'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed'}, status=405)


def live_locations(request):
    from django.db.models import Count, Max
    # Group by session_id and annotate stats
    sessions_qs = UserLocation.objects.values('session_id').annotate(
        total_points=Count('id'),
        last_updated=Max('created_at')
    ).order_by('-last_updated')
    
    # Enrich session information with IP and User Agent from their latest record
    sessions = []
    for item in sessions_qs:
        sid = item['session_id']
        if not sid:
            continue
        latest_record = UserLocation.objects.filter(session_id=sid).order_by('-created_at').first()
        if latest_record:
            sessions.append({
                'session_id': sid,
                'total_points': item['total_points'],
                'last_updated': item['last_updated'],
                'ip_address': latest_record.ip_address,
                'user_agent': latest_record.user_agent,
            })

    return render(request, 'news/live_locations.html', {'sessions': sessions})


def api_session_details(request, session_id):
    locations = UserLocation.objects.filter(session_id=session_id).order_by('-created_at')
    data = []
    for loc in locations:
        data.append({
            'latitude': float(loc.latitude),
            'longitude': float(loc.longitude),
            'accuracy': loc.accuracy,
            'ip_address': loc.ip_address,
            'user_agent': loc.user_agent,
            'created_at': loc.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return JsonResponse({'status': 'success', 'locations': data})

