from django.urls import path

from equip.views import (
    PressListView,
    PressDetailView,
)

from mtn.views import (
    OrderListView,
)

app_name = "equip"

urlpatterns = [
    path('equipment/', PressListView.as_view(), name='presslist'),
    path('equipment/press/<int:pk>', PressDetailView.as_view(), name='press'),
    path('equipment/press/<int:pk>/orders', OrderListView.as_view(),
         name='press-orders'),
]
