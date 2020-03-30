from django.contrib import admin

# Register your models here.

from staff.models import Employee

admin.site.register(Employee)
