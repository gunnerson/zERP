from django.contrib import admin

from mtn.models import Order

# class OrderAdmin(admin.ModelAdmin):
#     readonly_fields = ('date_added',)

admin.site.register(Order)
