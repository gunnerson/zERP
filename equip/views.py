from django.shortcuts import redirect, get_object_or_404
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
