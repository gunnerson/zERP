from django.urls import path

from invent.views import (
    PartListView,
    PartCreateView,
    PartDetailView,
    VendorCreateView,
    VendorDetailView,
    UsedPartListView,
)

app_name = "invent"

urlpatterns = [
    path('inventory/', PartListView.as_view(), name='partlist'),
    path('inventory/part/<int:pk>', PartDetailView.as_view(), name='part'),
    path('inventory/new_part/', PartCreateView.as_view(), name='new_part'),
    path('inventory/new_vendor/', VendorCreateView.as_view(),
         name='new_vendor'),
    path('inventory/vendor/<int:pk>', VendorDetailView.as_view(),
         name='vendor'),
    path('inventory/used_parts/', UsedPartListView.as_view(),
         name='usedpartlist'),

]
