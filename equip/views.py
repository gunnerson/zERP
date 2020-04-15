from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Press


class PressListView(LoginRequiredMixin, ListView):
    """List of equipment"""
    model = Press


class PressDetailView(LoginRequiredMixin, DetailView):
    """View part from the inventory"""
    model = Press
