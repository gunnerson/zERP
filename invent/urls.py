from django.urls import path

from . import views
from invent.views import PartListView

app_name = "invent"

urlpatterns = [
    path('inventory/', PartListView.as_view(), name='partlist'),
    path('inventory/new_part/', views.new_part, name='new_part'),
    path('inventory/new_vendor/', views.new_vendor, name='new_vendor'),

]
