from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomerUser

admin.site.register(CustomerUser, UserAdmin)
# Register your models here.
