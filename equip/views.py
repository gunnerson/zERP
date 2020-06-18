import calendar
import json
import hashlib
from django.shortcuts import redirect, render
from django.utils import timezone
from datetime import timedelta
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from pathlib import Path
from django.contrib import messages
from django.db.models import Q
from django.core import serializers
# from rest_framework import authentication, permissions

from .models import Press, Upload, Imprint
from mtn.models import Order, Pm
from mtn.cm import has_group, get_shift, is_valid_param, get_url_kwargs
from .forms import PressUpdateForm, UploadCreateForm
from invent.models import Part


class PressListView(LoginRequiredMixin, ListView):
    """List of equipment"""
    model = Press
    # paginate_by = 20

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(get_url_kwargs(self.request))
        return context

    def get_queryset(self):
        # Filter list by group
        qs = Press.objects.all()
        group = self.request.GET.get('grp', None)
        if group == 'on' or group is None:
            pass
        else:
            qs = qs.filter(group=group)
        return qs


class PressDetailView(LoginRequiredMixin, DetailView):
    """View part from the inventory"""
    model = Press

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # Get list of uploads
        uploads = self.object.upload_set.all()
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
        try:
            next_pm = self.object.next_pm()
            context['next_pm_id'] = next_pm.id
            context['next_pm_duedate'] = next_pm.due_date()
        except Pm.DoesNotExist:
            pass
        context['uploads'] = uploads
        context['dts_total'] = dts_total
        context['dts_last'] = dts_last
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
        uploads = press.upload_set.all()
        context['uploads'] = uploads
        return context

    # def post(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     # Delete uploads
    #     marked_uploads = request.POST.getlist('marked_upload', None)
    #     if marked_uploads is not None:
    #         uploads = Upload.objects.filter(press=self.object)
    #         for upload_id in marked_uploads:
    #             upload = uploads.get(id=upload_id)
    #             upload.file.delete(save=True)
    #             upload.delete()
    #     return super(PressUpdateView, self).post(request, *args, **kwargs)

    def test_func(self):
        return has_group(self.request.user, 'maintenance')


class UploadCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Upload a file"""
    model = Upload
    form_class = UploadCreateForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if 'equipment' in self.request.META['HTTP_REFERER']:
            press_id = self.kwargs['pk']
            context['press_id'] = press_id
        else:
            part_id = self.kwargs['pk']
            context['part_id'] = part_id
        return context

    def form_valid(self, form):
        # Check that upload description is unique and save
        self.object = form.save(commit=False)
        pk = self.kwargs['pk']
        if 'equipment' in self.request.META['HTTP_REFERER']:
            is_equip = True
            appname = 'equip'
            press = Press.objects.get(id=pk)
            uploads = press.upload_set.all()
        else:
            is_equip = False
            appname = 'invent'
            part = Part.objects.get(id=pk)
            uploads = part.upload_set.all()
        # Calculate file hash
        file = self.request.FILES['file']
        BLOCK_SIZE = 65536
        file_hash = hashlib.sha256()
        fb = file.read(BLOCK_SIZE)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = file.read(BLOCK_SIZE)
        hexhash = file_hash.hexdigest()
        try:
            origin = Upload.objects.get(uhash=hexhash)
        except Upload.DoesNotExist:
            taken_names = []
            for upload in uploads:
                taken_names.append(upload.descr)
            name = self.object.descr
            if name in taken_names:
                messages.add_message(self.request, messages.INFO,
                                     'File with this description already exists.')
                return redirect(self.request.META['HTTP_REFERER'])
            else:
                file_name = self.object.descr.replace(' ', '_').lower().strip()
                file_ext = Path(self.object.file.name).suffixes
                file_path = '{0}/{1}/{2}{3}'.format(appname, pk,
                                                    file_name, file_ext)
                self.object.file.name = file_path
                self.object.uhash = hexhash
                self.object.save()
                origin = self.object
        if is_equip:
            origin.press.add(press)
            return redirect('equip:press', pk=pk)
        else:
            origin.part.add(part)
            return redirect('invent:part', pk=pk)

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


def load_map(request):
    return render(request, 'equip/map.html')


class MapData(RetrieveAPIView):
    """Get data for floor map"""

    def get(self, request, *args, **kwargs):
        # Generate imprints from existing SVG
        # imprint_array = json.loads(request.GET['imprintArray'])
        # for imprint in imprint_array:
        #     press = Press.objects.get(id=imprint.get('press_id'))
        #     Imprint(
        #         press=press,
        #         x=int(imprint.get('x')),
        #         y=int(imprint.get('y')),
        #         width=int(imprint.get('width')),
        #         height=int(imprint.get('height'))
        #     ).save()
        imps = Imprint.objects.all()
        imps_json = serializers.serialize('json', imps)
        id_list = imps.values_list('press', flat=True)
        press_dict = {}
        qs = Press.objects.filter(id__in=id_list)
        shift = get_shift()
        for press in qs:
            press_dict[press.pk] = {}
            press_dict[press.pk].update({'status': press.status()})
            press_dict[press.pk].update({'name': press.pname})
            press_dict[press.pk].update(
                {'short_name': press.pname.split(' ')[-1]})
            job = press.job(shift=shift)
            if job is not None:
                if (job.start_time() < timezone.localtime(timezone.now()) and
                        job.end_time() >= timezone.localtime(timezone.now())):
                    press_dict[press.pk].update({'job': str(job)})
        data = {
            "impsDict": imps_json,
            "pressDict": press_dict,
        }
        return Response(data)
