# pyrefly: ignore [missing-import]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.news_detail, name='news_detail'),
    path('live-locations/', views.live_locations, name='live_locations'),
    path('api/save-location/', views.save_location, name='save_location'),
    path('api/session-details/<str:session_id>/', views.api_session_details, name='api_session_details'),
]
