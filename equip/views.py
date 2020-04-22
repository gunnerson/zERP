from django.http import JsonResponse
from datetime import date, timedelta
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

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

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        today = date.today()
        delta = timedelta(days=30)
        start_date = today - delta
        dts = []
        i = 0
        while i < 12:
            dt = Press.downtime(self, start_date, today)
            start_date -= delta
            today -= delta
            dts.append(dt)
            i += 1
        context['dts'] = dts
        return context


def get_data(request, *args, **kwargs):
    data = {
        "key": 100,
    }
    return JsonResponse(data)
