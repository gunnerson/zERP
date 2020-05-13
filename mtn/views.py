from django.shortcuts import render, redirect
from django.http import Http404
from datetime import date, timedelta
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from pathlib import Path
# from django.db.models import Q
from django.contrib.postgres.search import SearchRank, SearchVector, SearchQuery

from .models import Order, Image
from equip.models import Press
from invent.models import UsedPart
from staff.models import Employee
from .forms import OrderCreateForm, OrderUpdateForm, ImageCreateForm


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
    count = 0
    paginate_by = 20

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        press_excl = False
        search_exp = "collapse"
        if 'pk' in self.kwargs:
            press_id = self.kwargs['pk']
            press = Press.objects.get(id=self.kwargs['pk'])
            press_excl = True
            context['press_id'] = press_id
            context['press'] = press
        closed_checked = self.request.GET.get('closed')
        query = self.request.GET.get('query', None)
        if is_valid_queryparam(query):
            search_exp = "collapse show"
            context['query'] = query
            context['count'] = self.count or 0
        context['search_exp'] = search_exp
        context['closed_checked'] = closed_checked
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
        if is_valid_queryparam(query):
            query = SearchQuery(query)
            vector = SearchVector('textsearchable_index_col')
            qs = qs.annotate(rank=SearchRank(vector, query)).filter(
                textsearchable_index_col=query).order_by('-rank')
            # query_terms = query.split()
            # tsquery = " & ".join(query_terms)
            # tsquery += ":*"
            # qs = qs.extra(where=["textsearchable_index_col @@ (to_tsquery(%s)) = true"],
            #               params=[tsquery])
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

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        # If order type isn't "repair" disable "cause" field
        if (self.object.ordertype == "ST" or
                self.object.ordertype == "PM"):
            self.object.cause = "NW"
        self.object.save()
        return redirect('mtn:order-list')

    def get_form_kwargs(self, **kwargs):
        kwargs = super(OrderCreateView, self).get_form_kwargs()
        kwargs.update(request=self.request)
        return kwargs


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
                origin=Employee.objects.get(id=3),
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
