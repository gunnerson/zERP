import re
from django.shortcuts import render, redirect
from django.http import Http404
from datetime import timedelta
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from pathlib import Path

from .models import Order, Image, Downtime, Pm
from equip.models import Press
from staff.models import Employee
from .forms import OrderCreateForm, OrderUpdateForm, ImageCreateForm, PmForm
from .cm import dbsearch, has_group, is_valid_param, get_url_kwargs, \
    is_empty_param


def index(request):
    return render(request, 'mtn/index.html')


class OrderListView(LoginRequiredMixin, ListView):
    """List of existing work orders"""
    model = Order
    # count = 0
    paginate_by = 20

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        press_excl = False
        search_exp = "collapse"
        request = self.request
        context.update(get_url_kwargs(request))
        if 'pk' in self.kwargs:
            press_id = self.kwargs['pk']
            press = Press.objects.get(id=self.kwargs['pk'])
            press_excl = True
            context['press_id'] = press_id
            context['press'] = press
        query = context.get('query', None)
        if is_valid_param(query):
            search_exp = "collapse show"
            context['count'] = self.count or 0
        context['search_exp'] = search_exp
        context['press_excl'] = press_excl
        return context

    def get_queryset(self):
        qs = Order.objects.all()
        if 'pk' in self.kwargs:
            press = Press.objects.get(id=self.kwargs['pk'])
            qs = qs.filter(local=press)
        closed = self.request.GET.get('closed', False)
        if closed is False:
            qs = qs.exclude(closed=True)
        # Search orders
        query = self.request.GET.get('query', None)
        if is_valid_param(query):
            qs = dbsearch(qs, query, 'B', 'descr', 'descrrep')
            self.count = len(qs)
        return qs


class OrderDetailView(LoginRequiredMixin, DetailView):
    """View a work order"""
    model = Order

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        used_parts = self.object.usedpart_set.all()
        cost_of_repair = round(Order.cost_of_repair(self.object), 2)
        timereph = self.object.timerep
        if timereph is not None:
            timereph = timereph.total_seconds() / 3600
        images = Image.objects.filter(order=self.object.id)
        context['timereph'] = timereph
        context['used_parts'] = used_parts
        context['cost_of_repair'] = cost_of_repair
        context['images'] = images
        return context


class OrderCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a work order"""
    model = Order
    form_class = OrderCreateForm

    def test_func(self):
        return (has_group(self.request.user, 'maintenance') or
                has_group(self.request.user, 'supervisor'))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['group'] = self.request.GET.get('group')
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        if self.object.ordertype == "ST":
            self.object.cause = "NW"
        mold = form.cleaned_data.get('mold')
        if is_valid_param(mold):
            format_moldstr = re.sub(r'[\W_]+', '', mold).upper()
            try:
                press = Press.objects.get(pname=format_moldstr)
            except Press.DoesNotExist:
                press = Press(pname=format_moldstr, group='TL')
                press.save()
            self.object.local = press
        self.object.save()
        if self.object.status == 'DN':
            Downtime(order=self.object, start=timezone.now(),
                     dttype='DN').save()
        return redirect('mtn:order-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        press_id = self.kwargs.get('pk', None)
        kwargs.update(press_id=press_id)
        kwargs.update(request=self.request)
        return kwargs


@login_required
def load_locales(request):
    group = request.GET.get('group')
    subgroup = request.GET.get('subgroup')
    if group == 'PR' and is_valid_param(subgroup):
        locales = Press.objects.filter(group=group, subgroup=subgroup)
    else:
        locales = Press.objects.filter(group=group)
    return render(request, 'mtn/elements/local_dropdown_list_options.html',
                  {'locales': locales})


class OrderUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit a work order"""
    model = Order
    form_class = OrderUpdateForm
    template_name_suffix = '_update_form'

    def test_func(self):
        return has_group(self.request.user, 'maintenance')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # Convert repair time input to hours
        timerep = self.object.timerep
        if is_valid_param(timerep):
            timereph = timerep.seconds + timerep.microseconds / 1000000
            self.object.timerep = timedelta(hours=timereph)
        if self.object.closed:
            dt_sessions = Downtime.objects.filter(order=self.object)
            if dt_sessions.exists():
                last_dt_session = dt_sessions.last()
                if last_dt_session.end is None:
                    last_dt_session.end = timezone.now()
                    last_dt_session.save(update_fields=['end'])
                rep_dt_sessions = dt_sessions.filter(dttype='RE')
            if is_empty_param(timerep):
                rep_dur = timedelta()
                for session in rep_dt_sessions:
                    if (is_valid_param(session.start) and
                            is_valid_param(session.end)):
                        rep_dur += (session.end - session.start)
                self.object.timerep = rep_dur
            idle_dt_sessions = dt_sessions.exclude(dttype='RE')
            if idle_dt_sessions.exists():
                dt_dur = timedelta()
                for session in idle_dt_sessions:
                    if (is_valid_param(session.start) and
                            is_valid_param(session.end)):
                        dt_dur += (session.end - session.start)
                self.object.timerepidle = dt_dur
            else:
                self.object.timerepidle = timedelta()
            dt_sessions.delete()
            if is_empty_param(self.object.cause):
                self.object.cause = 'UN'
            self.object.status = 'SB'
        self.object.save()
        return redirect('mtn:order-list')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        timereph = self.object.timerep
        if timereph is not None:
            timereph = timereph.total_seconds() / 3600
        used_parts = self.object.usedpart_set.all()
        context['used_parts'] = used_parts
        context['timereph'] = timereph
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        dt_sessions = Downtime.objects.filter(order=self.object, dttype='RE')
        if dt_sessions.exists():
            has_dt = True
        else:
            has_dt = False
        kwargs.update(has_dt=has_dt)
        return kwargs


class ImageCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Upload an image"""
    model = Image
    form_class = ImageCreateForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['order_id'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        order_id = self.kwargs['pk']
        order = Order.objects.get(id=order_id)
        date = timezone.now()
        date = date.strftime("%Y-%m-%d")
        self.object = form.save(commit=False)
        file_ext = Path(self.object.image.name).suffixes
        self.object.order = order
        self.object.image.name = 'mtn/{0}/{1}{2}'.format(
            order.id, date, file_ext)
        self.object.save()
        return redirect('mtn:order', pk=order_id)

    def test_func(self):
        return has_group(self.request.user, 'maintenance')


@login_required
def repair_toggle(request, pk, func):
    order = Order.objects.get(id=pk)
    if func == 'start':
        new_status = 'RE'
        if order.repby is None:
            try:
                repby_initial = Employee.objects.get(user=request.user)
            except Employee.DoesNotExist:
                repby_initial = None
            if repby_initial is not None:
                order.repby = repby_initial
                order.save(update_fields=['repby'])
        Downtime(order=order, start=timezone.now(), dttype=new_status).save()
    elif func == 'stop':
        new_status = 'DN'
        pending_session = Downtime.objects.filter(order=order).last()
        if pending_session is not None:
            if is_empty_param(pending_session.end):
                pending_session.end = timezone.now()
                pending_session.save(update_fields=['end'])
        Downtime(order=order, start=timezone.now(), dttype=new_status).save()
    elif func == 'ready':
        new_status = 'SB'
        pending_session = Downtime.objects.filter(order=order).last()
        if pending_session is not None:
            if is_empty_param(pending_session.end):
                pending_session.end = timezone.now()
                pending_session.save(update_fields=['end'])
    else:
        new_status = 'AP'
        pending_session = Downtime.objects.filter(order=order).last()
        if pending_session is not None:
            if is_empty_param(pending_session.end):
                pending_session.end = timezone.now()
                pending_session.save(update_fields=['end'])
        Downtime(order=order, start=timezone.now(), dttype=new_status).save()
    order.status = new_status
    order.save(update_fields=['status'])
    return redirect('mtn:order-list')


@login_required
def create_pms(request):
    if has_group(request.user, 'maintenance'):
        presses = Press.objects.filter(group='PR')
        presses = presses.exclude(subgroup='OT')
        presses = presses.exclude(subgroup='PN')
        for press in presses:
            pms = Pm.objects.filter(local=press)
            if pms.exists() is False:
                Pm(
                    local=press,
                    pm_date=timezone.now().date(),
                    periodic=timedelta(days=180),
                ).save()
        return redirect('mtn:index')
    else:
        raise Http404


class PmListView(LoginRequiredMixin, ListView):
    """List of existing work orders"""
    model = Pm

    def get_queryset(self):
        qs = Pm.objects.all().order_by('pm_date', 'local')
        return qs


class PmUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit a pm order"""
    model = Pm
    form_class = PmForm
    template_name_suffix = '_update_form'

    def test_func(self):
        return has_group(self.request.user, 'maintenance')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        time_required = self.object.time_required
        if is_valid_param(time_required):
            time_requiredh = time_required.seconds + \
                time_required.microseconds / 1000000
            self.object.time_required = timedelta(hours=time_requiredh)
        self.object.save()
        if self.object.closed:
            Pm(
                local=self.object.local,
                pm_date=self.object.pm_date + self.object.periodic,
                time_required=self.object.time_required,
                periodic=self.object.periodic,
                descr=self.object.descr,
            ).save()
        return redirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['used_parts'] = self.object.usedpart_set.all()
        return context


@login_required
def bulk_update(request):
    # orders = Order.objects.all()
    # for order in orders:
    #     order.timerepidle = timedelta()
    #     order.save(update_fields=['timerepidle'])
    return redirect('mtn:index')
