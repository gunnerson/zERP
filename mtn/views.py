from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Order
from .forms import OrderForm, RepairForm

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

    def get_context_data(self, **kwargs):
        if (has_group(self.request.user, 'maintenance') or 
        has_group(self.request.user, 'supervisor')):
            context = super(OrderDetailView, self).get_context_data(**kwargs)

        else:
            raise Http404        

        return context
        
@login_required
def new_order(request):
    """Add new order"""
    if (has_group(request.user, 'maintenance') or 
        has_group(request.user, 'supervisor')):
    
        if request.method != 'POST':
            # No data submitted; create a blank form.
            form = OrderForm()

        else:
        # POST data submitted; process data.
            form = OrderForm(data=request.POST)
            if form.is_valid():
                new_order = form.save(commit=False)
                new_order.owner = request.user
                new_order.save()
                return HttpResponseRedirect(reverse('mtn:order-list'))
    
    else:
        raise Http404       
                                            
    context = {'form': form}
    return render(request, 'mtn/new_order.html', context)
    
@login_required
def edit_order(request, order_id):
    """Edit an existing repair."""
    if has_group(request.user, 'maintenance'):
        order = Order.objects.get(id=order_id)

        if request.method != 'POST':
            # Initial request; pre-fill form with the current repair.
            form = RepairForm(instance=order)

        else:
        # POST data submitted; process data.
            form = RepairForm(instance=order, data=request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('mtn:order',
                                                args=[order.id]))
    else:
        raise Http404

    context = {'order': order, 'form': form}
    return render(request, 'mtn/edit_order.html', context)  

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

