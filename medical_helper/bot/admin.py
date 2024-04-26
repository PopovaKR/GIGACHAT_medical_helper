from django.contrib import admin
from .models import RegisteredUser


@admin.register(RegisteredUser)
class RegisteredUserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'email', 'email_confirmed', 'developer_mode']
    search_fields = ['user_id', 'email']