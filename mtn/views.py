from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import CreateView, UpdateView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Order
from .forms import OrderCreateForm, OrderUpdateForm
from invent.models import Part, UsedPart


def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


def is_valid_queryparam(param):
    return param != '' and param is not None


def index(request):
    """The home page for EPR"""
    return render(request, 'mtn/index.html')


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    paginate_by = 10

    def get_queryset(self):
        qs = Order.objects.all().order_by('-date_added')
        check_closed = self.request.GET.get('check_closed')
        if is_valid_queryparam(check_closed):
            qs = qs.filter(closed=check_closed)
        else:
            qs = qs.filter(closed=False)
        return qs


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        used_parts = self.object.usedpart_set.all()
        cost_of_repair = round(Order.cost_of_repair(self), 2)
        context['used_parts'] = used_parts
        context['cost_of_repair'] = cost_of_repair
        return context


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderCreateForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        if has_group(self.request.user, 'maintenance'):
            return HttpResponseRedirect(self.get_success_url())
        else:
            return redirect('mtn:order-list')

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(OrderCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['owner'] = self.request.user
        return kwargs


class OrderUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Order
    form_class = OrderUpdateForm
    template_name_suffix = '_update_form'

    def test_func(self):
        if has_group(self.request.user, 'maintenance'):
            return redirect('mtn:order-list')


# class AddPartView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#     model = Order
#     form_class = AddPartForm
#     template_name_suffix = '_add_part'

#     def test_func(self):
#         if has_group(self.request.user, 'maintenance'):
#             return redirect('mtn:order-list')

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs.update(request=self.request)
#         return kwargs

