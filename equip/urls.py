from django.urls import path

from equip.views import (
    PressListView,
    PressDetailView,
)

app_name = "equip"

urlpatterns = [
    path('equipment/', PressListView.as_view(), name='presslist'),
    path('equipment/press/<int:pk>', PressDetailView.as_view(), name='press'),
]
