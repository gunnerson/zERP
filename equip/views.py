import calendar
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from pathlib import Path
from django.contrib import messages
# from rest_framework import authentication, permissions

from .models import Press, Upload
from mtn.models import Order
from mtn.views import has_group
from .forms import PressUpdateForm, UploadCreateForm


class PressListView(LoginRequiredMixin, ListView):
    """List of equipment"""
    model = Press
    # paginate_by = 20


class PressDetailView(LoginRequiredMixin, DetailView):
    """View part from the inventory"""
    model = Press

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # Get list of uploads
        uploads = Upload.objects.filter(press=self.object.id)
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
        context['uploads'] = uploads
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

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        press = self.get_object()
        uploads = Upload.objects.filter(press=press)
        context['uploads'] = uploads
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        uploads = Upload.objects.filter(press=self.object)
        marked_uploads = request.POST.getlist('marked_upload', None)
        if marked_uploads is not None:
            for upload_id in marked_uploads:
                upload = uploads.get(id=upload_id)
                upload.file.delete(save=True)
                upload.delete()
        return super(PressUpdateView, self).post(request, *args, **kwargs)

    def test_func(self):
        return has_group(self.request.user, 'maintenance')


class UploadCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Upload a file"""
    model = Upload
    form_class = UploadCreateForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        press_id = self.kwargs['pk']
        context['press_id'] = press_id
        return context

    def form_valid(self, form):
        press_id = self.kwargs['pk']
        press = Press.objects.get(id=press_id)
        uploads = press.upload_set.all()
        taken_names = []
        for upload in uploads:
            taken_names.append(upload.descr)
        self.object = form.save(commit=False)
        name = self.object.descr
        if name in taken_names:
            messages.add_message(self.request, messages.INFO,
                                 'File with this description already exists.')
            return redirect(self.request.META['HTTP_REFERER'])
        else:
            file_name = self.object.descr.replace(' ', '_').lower().strip()
            file_ext = Path(self.object.file.name).suffixes
            file_path = 'equip/{0}/{1}{2}'.format(press.id,
                                                  file_name, file_ext)
            self.object.press = press
            self.object.file.name = file_path
            self.object.save()
            return redirect('equip:press', pk=press_id)

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
