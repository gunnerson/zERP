from django.shortcuts import render, redirect
from django.http import Http404
from datetime import date, timedelta
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from pathlib import Path

from .models import Order, Image, Downtime
from equip.models import Press
from invent.models import UsedPart
from staff.models import Employee
from .forms import OrderCreateForm, OrderUpdateForm, ImageCreateForm
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
        # If order type isn't "repair" disable "cause" field
        if (self.object.ordertype == "ST" or
                self.object.ordertype == "PM"):
            self.object.cause = "NW"
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


@login_required
def add_pm(request, pk):
    if has_group(request.user, 'maintenance'):
        press = Press.objects.get(id=pk)
        orders = press.order_set.filter(
            closed=True,
            ordertype='PM'
        )
        if orders.exists():
            last_pm = orders.last()
            used_parts = UsedPart.objects.filter(order_id=last_pm.pk)
            new_pm = last_pm
            new_pm.pk = None
            new_pm.owner = request.user
            new_pm.date_added = timezone.now()
            new_pm.repdate = None
            new_pm.repby = None
            new_pm.closed = False
            new_pm.save()
            for part in used_parts:
                new_part = part
                new_part.pk = None
                new_part.order_id = new_pm.id
                new_part.save()
        else:
            new_pm = Order(
                owner=request.user,
                # origin=Employee.objects.get(id=3),
                local=press,
                ordertype='PM',
                cause='NW',
                descr='List PM procedures here',
            )
            new_pm.save()
    else:
        raise Http404
    return redirect('mtn:order-list')


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
            # Calculate DT and delete DT sessions
            dt_sessions = Downtime.objects.filter(order=self.object)
            rep_dur = timedelta()
            last_dt_session = dt_sessions.last()
            first_dt_session = dt_sessions.first()
            rep_dt_sessions = dt_sessions.filter(dttype='RE')
            if dt_sessions.exists():
                if last_dt_session.end is None:
                    last_dt_session.end = timezone.now()
                    last_dt_session.save(update_fields=['end'])
            if is_empty_param(timerep):
                if rep_dt_sessions.exists():
                    for session in rep_dt_sessions:
                        if (is_valid_param(session.start) and
                                is_valid_param(session.end)):
                            rep_dur += (session.end - session.start)
                        else:
                            rep_dur += timedelta()
                    self.object.timerep = rep_dur
            if dt_sessions.exists() and is_valid_param(self.object.timerep):
                self.object.timerepidle = last_dt_session.end - \
                    first_dt_session.start - self.object.timerep
            elif is_valid_param(timerep):
                self.object.timerepidle = timezone.now() - \
                    self.object.date_added - self.object.timerep
            else:
                self.object.timerepidle = timezone.now() - \
                    self.object.date_added
            if self.object.timerepidle < timedelta():
                self.object.timerepidle = timedelta()
            dt_sessions.delete()
            if is_empty_param(self.object.cause):
                self.object.cause = 'UN'
            self.object.status = 'SB'
        self.object.save()
        return redirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        timereph = self.object.timerep
        if timereph is not None:
            timereph = timereph.total_seconds() / 3600
        context['timereph'] = timereph
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        dt_sessions = Downtime.objects.filter(order=self.object)
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
