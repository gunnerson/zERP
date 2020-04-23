import calendar
from django.utils import timezone
from datetime import timedelta
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
# from rest_framework import authentication, permissions

from .models import Press
from mtn.models import Order


class PressListView(LoginRequiredMixin, ListView):
    """List of equipment"""
    model = Press

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        orders = Order.objects.filter(closed=False)
        context['orders'] = orders
        return context

    def get_queryset(self):
        # Sort by status
        qs = Press.objects.all().order_by('-status')
        return qs


class PressDetailView(LoginRequiredMixin, DetailView):
    """View part from the inventory"""
    model = Press


class DowntimeChartData(RetrieveAPIView):
    """Get data for downtime chart"""
    # authentication_classes = []
    # permission_classes = []
    lookup_field = 'pk'
    queryset = Press.objects.all()

    def get(self, request, *args, **kwargs):
        today = timezone.now()
        month = today.month
        year = today.year
        dts = []
        labels =[]
        i = 0
        while i < 12:
            dt = Press.downtime(self, month, year)
            dts.append(dt)
            month_name = calendar.month_abbr[month]
            labels.append(month_name)
            month -= 1
            if month == 0:
                month = 12
                year -= 1
            i += 1
        data = {
            "labels": labels,
            "default": dts,
        }
        return Response(data)
