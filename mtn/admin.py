from django.contrib import admin

from mtn.models import Order, Image, Downtime

# class OrderAdmin(admin.ModelAdmin):
#     readonly_fields = ('date_added',)

admin.site.register(Order)
admin.site.register(Image)
admin.site.register(Downtime)

