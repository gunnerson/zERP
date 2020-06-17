from django.contrib import admin

from mtn.models import Order, Image, Downtime, Pm

# class OrderAdmin(admin.ModelAdmin):
#     readonly_fields = ('date_added',)

admin.site.register(Order)
admin.site.register(Image)
admin.site.register(Downtime)
admin.site.register(Pm)
