# pyrefly: ignore [missing-import]
from django.contrib import admin

from .models import UserLocation

@admin.register(UserLocation)
class UserLocationAdmin(admin.ModelAdmin):
    list_display = ('latitude', 'longitude', 'accuracy', 'ip_address', 'created_at')
    list_filter = ('created_at',)
    readonly_fields = ('latitude', 'longitude', 'accuracy', 'ip_address', 'user_agent', 'created_at')
