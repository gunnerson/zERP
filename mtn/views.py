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
from .cm import dbsearch, has_group, is_valid_param, get_url_kwargs


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
                     dt_status='PE').save()
        return redirect('mtn:order-list')


@login_required
def load_locales(request):
    group = request.GET.get('group')
    subgroup = request.GET.get('subgroup')
    if group == 'PR' and is_valid_param(subgroup):
        locales = Press.objects.filter(group=group, subgroup=subgroup)
    else:
        locales = Press.objects.filter(group=group)
    return render(request, 'mtn/local_dropdown_list_options.html',
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
        """If order closed fill empty repair date and cause"""
        check_closed = self.request.POST.get('check_closed', None)
        timereph = self.request.POST.get('timereph', None)
        self.object = form.save(commit=False)
        if check_closed is not None:
            self.object.closed = True
            if self.object.repdate == '' or self.object.repdate is None:
                self.object.repdate = date.today()
            if self.object.cause == '' or self.object.cause is None:
                self.object.cause = 'UN'
            if timereph == '' or timereph is None:
                self.object.timerep = timezone.now() - self.object.date_added
            dt_session = Downtime.objects.filter(order=self.object).last()
            dt_session.end = timezone.now()
            dt_session.save(update_fields=['end'])
            self.object.status = 'SB'
        if timereph != '' and timereph is not None:
            self.object.timerep = timedelta(hours=float(timereph))
        self.object.save()
        return redirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        timereph = self.object.timerep
        if timereph is not None:
            timereph = timereph.total_seconds() / 3600
        context['timereph'] = timereph
        return context


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
def start_repair(request, pk):
    order = Order.objects.get(id=pk)
    pending_session = Downtime.objects.filter(order=order).last()
    pending_session.end = timezone.now()
    pending_session.save(update_fields=['end'])
    Downtime(order=order,
             start=timezone.now(),
             dt_status='RE',
             owner=request.user,
             ).save()
    order.status = 'DN'
    order.save(update_fields=['status'])


@login_required
def end_repair(request, pk):
    order = Order.objects.get(id=pk)
    pending_session = Downtime.objects.filter(order_id=pk).last()
    pending_session.end = timezone.now()
    pending_session.save(update_fields=['end'])
    Downtime(order=order,
             start=timezone.now(),
             dt_status='PE',
             ).save()


@login_required
def order_status(request, pk):
    order = Order.objects.get(id=pk)
    order.status = request.GET.get('order_status')
    order.save(update_fields=['status'])
