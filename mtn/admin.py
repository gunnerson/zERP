from django.contrib import admin

# Register your models here for the admin site

from mtn.models import Order

admin.site.register(Order)
