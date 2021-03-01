import calendar
import hashlib
from datetime import datetime, date
from django.shortcuts import redirect, render
from django.utils import timezone
from django.urls import reverse_lazy
from datetime import timedelta
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from pathlib import Path
from django.contrib import messages
from django.core import serializers
from django.utils.safestring import mark_safe
# from rest_framework import authentication, permissions

from .models import Press, Upload, Imprint, Pmproc, Pmsched
from mtn.models import Order
from mtn.cm import has_group, get_url_kwargs, is_empty_param, get_shift
from .forms import PressUpdateForm, UploadCreateForm, PmschedCreateForm, \
    PmprocCreateForm, PmprocUpdateForm, PressCreateForm
from invent.models import Part, UsedPart
from .utils import Calendar
from prod.models import JobInst


class PressListView(LoginRequiredMixin, ListView):
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
            if group == 'PM':
                qs = Press.objects.filter(pmed=True)
            else:
                qs = qs.filter(group=group)
        return qs


class PressCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Press
    form_class = PressCreateForm

    def test_func(self):
        return has_group(self.request.user, 'maintenance')


class PressDetailView(LoginRequiredMixin, DetailView):
    model = Press

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
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
        cost_this_year = 0
        cost_last_year = 0
        start_date = today - timedelta(days=365)
        end_date = today
        orders = self.object.order_set.all()
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
        context['pmprocs'] = self.object.pmproc_set.all().order_by('pk')
        context['uploads'] = self.object.upload_set.all()
        context['images'] = self.object.image_set.all()
        context['parts'] = self.object.part_set.all()
        context['dts_total'] = dts_total
        context['dts_last'] = dts_last
        context['cost_this_year'] = cost_this_year
        context['cost_last_year'] = cost_last_year
        return context


class PressUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Press
    form_class = PressUpdateForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        press = self.get_object()
        uploads = press.upload_set.all()
        context['uploads'] = uploads
        return context

    def test_func(self):
        return has_group(self.request.user, 'maintenance')


class UploadCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
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
    # authentication_classes = []
    # permission_classes = []
    lookup_field = 'pk'
    queryset = Press.objects.all()

    def get(self, request, *args, **kwargs):
        today = timezone.now()
        month = today.month
        year = today.year
        dts = []
        labels = []
        phs = []
        i = 0
        while i < 12:
            dt = Press.downtime(self, month, year)
            dt = round(dt, 1)
            dts.append(dt)
            ph = Press.prod_hours(self, month, year)
            phs.append(ph)
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
            "phs": phs,
        }
        return Response(data)


def load_map(request):
    return render(request, 'equip/map.html')


class MapData(RetrieveAPIView):

    def get(self, request, *args, **kwargs):
        imps = Imprint.objects.all()
        imps_json = serializers.serialize('json', imps)
        id_list = imps.values_list('press', flat=True)
        press_dict = {}
        shift=get_shift()
        qs = Press.objects.filter(id__in=id_list)
        for press in qs:
            press_dict[press.pk] = {}
            if press.pm_today():
                press_dict[press.pk].update({'status': 'PM'})
            else:
                press_dict[press.pk].update({'status': press.status()})
            press_dict[press.pk].update({'name': press.pname})
            pm_prior = press.pm_prior()
            if pm_prior > 0 and press.pm_due():
                job = None
                job2 = None
                try:
                    job = press.job()
                except (JobInst.DoesNotExist, Press.DoesNotExist):
                    pass
                if job is None:
                    try:
                        job2 = press.joined.job()
                    except (JobInst.DoesNotExist, Press.DoesNotExist, AttributeError):
                        pass
                    if job2 is None:
                        press_dict[press.pk].update({'pmd': pm_prior})
            press_dict[press.pk].update(
                {'short_name': press.pname.split(' ')[-1]})
            if press.job(shift=shift) is not None:
                press_dict[press.pk].update({'job': 'Production'})
        data = {
            "impsDict": imps_json,
            "pressDict": press_dict,
        }
        return Response(data)


class PmListView(LoginRequiredMixin, ListView):
    model = Pmproc
    template_name = 'equip/press_pm.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        press_id = self.kwargs['pk']
        context['press_id'] = press_id
        context['press'] = Press.objects.get(id=press_id)
        return context

    def get_queryset(self):
        press_id = self.kwargs['pk']
        qs = Pmproc.objects.filter(local=press_id).order_by('pk')
        return qs


class PmprocCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Pmproc
    form_class = PmprocCreateForm

    def test_func(self):
        return has_group(self.request.user, 'maintenance')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        press_id = self.kwargs['pk']
        context['press_id'] = press_id
        context['press'] = Press.objects.get(id=press_id)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        press_id = self.kwargs['pk']
        press = Press.objects.get(id=press_id)
        self.object.local = press
        self.object.hours = self.object.freq
        self.object.save()
        if self.object.pm_part is not None:
            part = self.object.pm_part
            part.cat.add(press)
        return redirect('equip:press-pm', pk=press_id)


class PmprocUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Pmproc
    form_class = PmprocUpdateForm
    template_name = 'equip/pmproc_update_form.html'

    def test_func(self):
        return has_group(self.request.user, 'maintenance')

    def form_valid(self, form):
        self.object = form.save()
        if is_empty_param(self.object.descr):
            self.object.delete()
        if self.object.pm_part is not None:
            part = self.object.pm_part
            part.cat.add(self.object.local)
        return redirect('equip:press-pm', pk=self.object.local.id)


class PmschedCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Pmsched
    form_class = PmschedCreateForm

    def test_func(self):
        return (has_group(self.request.user, 'maintenance') or
                has_group(self.request.user, 'supervisor'))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        press_id = self.kwargs['pk']
        context['press_id'] = press_id
        context['press'] = Press.objects.get(id=press_id)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        press_id = self.kwargs['pk']
        press = Press.objects.get(id=press_id)
        self.object.local = press
        self.object.save()
        return redirect('equip:calendar')


class PmschedDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Pmsched
    success_url = reverse_lazy('equip:calendar')

    def test_func(self):
        return has_group(self.request.user, 'maintenance')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        press = self.object.local
        context['press_id'] = press.id
        context['press'] = press
        return context


class PmschedDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Pmsched

    def test_func(self):
        return has_group(self.request.user, 'maintenance')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        press_id = self.object.local.id
        press = Press.objects.get(id=press_id)
        procs = press.pmproc_set.all()
        context['press_id'] = press_id
        context['press'] = press
        context['procs'] = procs
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        press_id = self.object.local.id
        press = Press.objects.get(id=press_id)
        procs = press.pmproc_set.all()
        for proc in procs:
            marked = self.request.GET.get('resid_{0}'.format(proc.id), None)
            if marked:
                if proc.pm_part is not None:
                    if proc.pm_part.amount >= proc.pm_part_amount:
                        UsedPart(
                            part=proc.pm_part,
                            pm=self.object,
                            amount_used=proc.pm_part_amount
                        ).save()
                        proc.pm_part.amount -= proc.pm_part_amount
                        proc.pm_part.save(update_fields=['amount'])
                        proc.hours = 0
                        proc.save(update_fields=['hours'])
                    else:
                        messages.add_message(request, messages.INFO,
                                             'Not enough items "{0}" in stock'.format(proc.pm_part))
                else:
                    proc.hours = 0
                    proc.save(update_fields=['hours'])
        return self.render_to_response(context)


class CalendarView(LoginRequiredMixin, ListView):
    model = Pmsched
    template_name = 'equip/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month
