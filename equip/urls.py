from django.urls import path

from equip.views import (
    PressListView,
    PressDetailView,
    PressUpdateView,
    DowntimeChartData,
    UploadCreateView,
    load_map,
    MapData,
    PmListView,
    PmschedCreateView,
    CalendarView,
    PmschedDetailView,
    PmprocCreateView,
)

from mtn.views import OrderListView

app_name = "equip"

urlpatterns = [
    path('equipment/list', PressListView.as_view(), name='presslist'),
    path('equipment/map', load_map, name='load_map'),
    path('api/data/equipment/map', MapData.as_view(), name='map-data'),
    path('equipment/press/<int:pk>/', PressDetailView.as_view(), name='press'),
    path('equipment/press/<int:pk>/orders/', OrderListView.as_view(),
         name='press-orders'),
    path('equipment/press/<int:pk>/pm/', PmListView.as_view(),
         name='press-pm'),
    path('equipment/press/<int:pk>/add_pm/', PmprocCreateView.as_view(),
         name='add-pm'),
    path('equipment/press/<int:pk>/notes/', PressUpdateView.as_view(
        template_name='equip/press_update_form.html'),
        name='notes'),
    path('equipment/press/<int:pk>/upload/', UploadCreateView.as_view(),
         name='upload'),
    # path('equipment/press/<int:pk>/delete-upload/', PressUpdateView.as_view(
    #     template_name='equip/press_delete_upload.html'),
    #     name='delete-upload'),
    path('api/data/equipment/press/<int:pk>/',
         DowntimeChartData.as_view(), name='chart-data'),
    path('equipment/press/<int:pk>/schedule-pm/', PmschedCreateView.as_view(), name='pmsched'),
    path('equipment/pm/<int:pk>/', PmschedDetailView.as_view(), name='pm-detail'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
]
