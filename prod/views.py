from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Job, JobInst
from mtn.cm import has_group


class JobListView(LoginRequiredMixin, ListView):
    """List of jobs"""
    model = Job
    # paginate_by = 20


class JobDetailView(LoginRequiredMixin, DetailView):
    """View job"""
    model = Job


class JobCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Upload a file"""
    model = Job

    def test_func(self):
        return has_group(self.request.user, 'maintenance')


class JobUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Add notes"""
    model = Job

    def test_func(self):
        return has_group(self.request.user, 'maintenance')


class JobInstListView(LoginRequiredMixin, ListView):
    """List of jobs"""
    model = JobInst
    # paginate_by = 20


class JobInstDetailView(LoginRequiredMixin, DetailView):
    """View job"""
    model = JobInst


class JobInstCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Upload a file"""
    model = JobInst

    def test_func(self):
        return has_group(self.request.user, 'manager')


class JobInstUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Add notes"""
    model = JobInst

    def test_func(self):
        return has_group(self.request.user, 'manager')
