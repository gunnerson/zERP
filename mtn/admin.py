from django.contrib import admin

from mtn.models import Order, Image

# class OrderAdmin(admin.ModelAdmin):
#     readonly_fields = ('date_added',)

admin.site.register(Order)
admin.site.register(Image)
