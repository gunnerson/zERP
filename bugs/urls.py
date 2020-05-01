from django.urls import path

from .views import BugCreateView

app_name = "bugs"

urlpatterns = [
    path('report-bug/', BugCreateView.as_view(), name='report-bug'),

]
