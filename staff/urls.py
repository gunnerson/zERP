from django.urls import path

from .views import employees

app_name = "staff"

urlpatterns = [

    path('staff/', employees, name='staff'),

]
