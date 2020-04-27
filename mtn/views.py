from django.shortcuts import render, redirect
from django.http import Http404
from datetime import date, timedelta
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required

from .models import Order
from equip.models import Press
from .forms import OrderCreateForm, OrderUpdateForm
from staff.models import Employee


def has_group(user, group_name):
    # Check if the user belongs to a certain group
    return user.groups.filter(name=group_name).exists()


def is_valid_queryparam(param):
    # Check that returned parameter is valid
    return param != '' and param is not None


def index(request):
    return render(request, 'mtn/index.html')


class OrderListView(LoginRequiredMixin, ListView):
    """List of existing work orders"""
    model = Order
    paginate_by = 20

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        press_excl = False
        if 'pk' in self.kwargs:
            press_id = self.kwargs['pk']
            press_excl = True
            context['press_id'] = press_id
        check_closed = self.request.GET.get('check_closed')
        context['check_closed'] = check_closed
        context['press_excl'] = press_excl
        return context

    def get_queryset(self):
        qs = Order.objects.all().order_by('-id')
        if 'pk' in self.kwargs:
            press = Press.objects.get(id=self.kwargs['pk'])
            qs = qs.filter(local=press)
        else:
            check_closed = self.request.GET.get('check_closed')
            if is_valid_queryparam(check_closed):
                qs = qs.filter(closed=check_closed)
            else:
                qs = qs.filter(closed=False)
        return qs


class OrderDetailView(LoginRequiredMixin, DetailView):
    """View a work order"""
    model = Order

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        used_parts = self.object.usedpart_set.all()
        cost_of_repair = round(Order.cost_of_repair(self), 2)
        timereph = self.object.timerep
        if timereph is not None:
            timereph = timereph.total_seconds() / 3600
        context['timereph'] = timereph
        context['used_parts'] = used_parts
        context['cost_of_repair'] = cost_of_repair
        return context


class OrderCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a work order"""
    model = Order
    form_class = OrderCreateForm

    def test_func(self):
        return (has_group(self.request.user, 'maintenance') or
                has_group(self.request.user, 'supervisor'))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        # If order type isn't "repair" disable "cause" field
        if (self.object.ordertype == "ST" or
                self.object.ordertype == "PM"):
            self.object.cause = "NW"
        return redirect('mtn:order-list')


@login_required
def add_pm(request, pk):
    if has_group(request.user, 'maintenance'):
        order = Order(
            owner=request.user,
            origin=Employee.objects.get(id=3),
            local=Press.objects.get(id=pk),
            ordertype='PM',
            cause='NW',
            descr='Preventive maintenance',
        )
        order.save()
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

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs.update(request=self.request)
    #     return kwargs
