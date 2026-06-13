from django.urls import path
from . import views

urlpatterns = [
    path('', views.news_detail, name='news_detail'),
    path('api/save-location/', views.save_location, name='save_location'),
]
