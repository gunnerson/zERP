from django.urls import path

from .views import upload_sched, ScheduleView, generate_schedule

app_name = "prod"

urlpatterns = [
    path('production/upload', upload_sched, name='upload'),
    path('production/generate', generate_schedule, name='sched_gen'),
    path('production/schedule', ScheduleView.as_view(), name='prod_sched'),
]