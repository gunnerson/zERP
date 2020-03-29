from django.contrib import admin

# Register your models here for the admin site

from mtn.models import Order, Entry, Repair

admin.site.register(Order)
admin.site.register(Entry)
admin.site.register(Repair)
