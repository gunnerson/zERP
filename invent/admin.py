from django.contrib import admin

from invent.models import Part, Vendor, UsedPart

admin.site.register(Part)
admin.site.register(Vendor)
admin.site.register(UsedPart)
