from django.urls import path

from equip.views import (
    PressListView,
    PressDetailView,
    PressUpdateView,
    DowntimeChartData,
)

from mtn.views import (
    OrderListView,
    add_pm,
)

app_name = "equip"

urlpatterns = [
    path('equipment/', PressListView.as_view(), name='presslist'),
    path('equipment/press/<int:pk>/', PressDetailView.as_view(), name='press'),
    path('equipment/press/<int:pk>/add_pm/', add_pm,
         name='add_pm'),
    path('equipment/press/<int:pk>/orders/', OrderListView.as_view(),
         name='press-orders'),
    path('equipment/press/<int:pk>/notes/', PressUpdateView.as_view(
        template_name='equip/press_update_form.html'),
        name='notes'),
    path('api/data/equipment/press/<int:pk>/',
         DowntimeChartData.as_view(), name='chart-data'),
]
