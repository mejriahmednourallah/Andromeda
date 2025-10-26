from django.contrib import admin
from .models import FocusCategory, FocusSession


@admin.register(FocusCategory)
class FocusCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'created_at']
    search_fields = ['name']


@admin.register(FocusSession)
class FocusSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'duration', 'status', 'start_time']
    list_filter = ['status', 'category', 'start_time']
    search_fields = ['user__username', 'notes']
    date_hierarchy = 'start_time'
