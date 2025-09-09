from django.contrib import admin

# Register your models here.
# accounts/admin.py

from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'birth_date']
    search_fields = ['user__username', 'location']
    list_filter = ['birth_date']