import calendar
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
# from rest_framework import authentication, permissions

from .models import Press
from mtn.models import Order
from mtn.views import has_group
from .forms import PressUpdateForm


class PressListView(LoginRequiredMixin, ListView):
    """List of equipment"""
    model = Press
    # paginate_by = 20


class PressDetailView(LoginRequiredMixin, DetailView):
    """View part from the inventory"""
    model = Press

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # Calculate downtime per year
        today = timezone.now()
        month = today.month
        year = today.year
        dts_total = 0
        dts_last = 0
        i = month
        while i > 0:
            dt = Press.downtime(self, month, year)
            dts_total += dt
            month -= 1
            i -= 1
        month = 12
        year -= 1
        while i < 12:
            dt = Press.downtime(self, month, year)
            dts_last += dt
            month -= 1
            i += 1
        # Last PM date
        last_pm = Press.last_pm(self)
        # Calculate repair costs
        cost_this_year = 0
        cost_last_year = 0
        start_date = today - timedelta(days=365)
        end_date = today
        orders = Order.objects.filter(local=self.object.id)
        this_year = orders.filter(
            date_added__range=(start_date, end_date)
        )
        start_date -= timedelta(days=365)
        end_date -= timedelta(days=365)
        last_year = orders.filter(
            date_added__range=(start_date, end_date)
        )
        for order in this_year:
            cost_this_year += round(Order.cost_of_repair(order), 2)
        for order in last_year:
            cost_last_year += round(Order.cost_of_repair(order), 2)
        context['dts_total'] = dts_total
        context['dts_last'] = dts_last
        context['last_pm'] = last_pm
        context['cost_this_year'] = cost_this_year
        context['cost_last_year'] = cost_last_year
        return context


class PressUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Add notes"""
    model = Press
    form_class = PressUpdateForm
    template_name = 'equip/press_update_form.html'

    def test_func(self):
        return has_group(self.request.user, 'maintenance')


class DowntimeChartData(RetrieveAPIView):
    """Get data for downtime chart"""
    # authentication_classes = []
    # permission_classes = []
    lookup_field = 'pk'
    queryset = Press.objects.all()

    def get(self, request, *args, **kwargs):
        # Calculate downtime
        today = timezone.now()
        month = today.month
        year = today.year
        dts = []
        labels = []
        i = 0
        while i < 12:
            dt = Press.downtime(self, month, year)
            dt = round(dt, 1)
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
