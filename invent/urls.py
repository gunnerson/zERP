from django.urls import path

from invent.views import (
    PartListView,
    PartCreateView,
    VendorCreateView,
    )

app_name = "invent"

urlpatterns = [
    path('inventory/', PartListView.as_view(), name='partlist'),
    path('inventory/new_part/', PartCreateView.as_view(), name='new_part'),
    path('inventory/new_vendor/', VendorCreateView.as_view(), name='new_vendor'),

]
