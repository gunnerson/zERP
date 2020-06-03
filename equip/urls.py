from django.urls import path

from equip.views import (
    PressListView,
    PressDetailView,
    PressUpdateView,
    DowntimeChartData,
    UploadCreateView,
    load_map,
)

from mtn.views import (
    OrderListView,
    add_pm,
)

app_name = "equip"

urlpatterns = [
    path('equipment/', PressListView.as_view(), name='presslist'),
    path('equipment/map', load_map, name='load_map'),
    path('equipment/press/<int:pk>/', PressDetailView.as_view(), name='press'),
    path('equipment/press/<int:pk>/add_pm/', add_pm,
         name='add_pm'),
    path('equipment/press/<int:pk>/orders/', OrderListView.as_view(),
         name='press-orders'),
    path('equipment/press/<int:pk>/notes/', PressUpdateView.as_view(
        template_name='equip/press_update_form.html'),
        name='notes'),
    path('equipment/press/<int:pk>/upload/', UploadCreateView.as_view(),
         name='upload'),
    path('equipment/press/<int:pk>/delete-upload/', PressUpdateView.as_view(
        template_name='equip/press_delete_upload.html'),
        name='delete-upload'),
    path('api/data/equipment/press/<int:pk>/',
         DowntimeChartData.as_view(), name='chart-data'),
]
