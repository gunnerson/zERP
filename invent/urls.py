from django.urls import path

from . import views
from invent.views import PartsList

app_name = "invent"

urlpatterns = [
    path('inventory/', PartsList, name='partslist'),
    path('inventory/new_part/', views.new_part, name='new_part'),
    path('inventory/new_vendor/', views.new_vendor, name='new_vendor'),

]
