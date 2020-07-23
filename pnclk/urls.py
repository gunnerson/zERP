from django.urls import path

from .views import GetID, AddRecord

app_name = "pnclk"

urlpatterns = [
    path('pnclk/', GetID, name='index'),
    path('pnclk/<int:pk>/', AddRecord, name='rec'),
]
