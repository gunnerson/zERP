from django.urls import path

from invent.views import (
    PartListView,
    PartCreateView,
    PartDetailView,
    PartUpdateView,
    VendorListView,
    VendorCreateView,
    VendorDetailView,
    VendorUpdateView,
)

from equip.views import UploadCreateView

app_name = "invent"

urlpatterns = [
    path('inventory/', PartListView.as_view(), name='partlist'),
    path('inventory/part/<int:pk>', PartDetailView.as_view(), name='part'),
    path('inventory/part/<int:pk>/edit', PartUpdateView.as_view(),
         name='edit_part'),
    path('inventory/part/<int:pk>/upload/', UploadCreateView.as_view(),
         name='upload'),
    path('inventory/new_part/', PartCreateView.as_view(), name='new_part'),
    path('inventory/vendors/', VendorListView.as_view(), name='vendor-list'),
    path('inventory/new_vendor/', VendorCreateView.as_view(),
         name='new_vendor'),
    path('inventory/vendor/<int:pk>', VendorDetailView.as_view(),
         name='vendor'),
    path('inventory/vendor/<int:pk>/edit', VendorUpdateView.as_view(),
         name='edit_vendor'),
]
