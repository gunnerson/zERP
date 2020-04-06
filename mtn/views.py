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

def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 

def is_valid_queryparam(param):
    return param != '' and param is not None
    
def index(request):
    """The home page for EPR"""
    return render(request, 'mtn/index.html')

@login_required
def maint(request):
    """The home page for Maintenance"""
    return render(request, 'mtn/maint.html')
    
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    paginate_by = 5
 
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


# def add_part(request, order_id):
#   order = Order.objects.get(pk=order_id)
#   PartFormset = inlineformset_factory(Order, Part, fields=('partname',), extra=1)

#   if request.method == 'POST':
#       formset = PartFormset(request.POST, instance=order)
#       if formset.is_valid():
#           formset.save
#           return redirect('', order_id=order.id)

# formset = PartFormset(instance=order)

# return render(request, 'index.html', {'formset': formset})

