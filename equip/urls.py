from django.urls import path

from .views import equip

app_name = "equip"

urlpatterns = [

    path('equipment/', equip, name='equip'),

]
