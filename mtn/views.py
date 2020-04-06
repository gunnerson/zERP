from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory

from .models import Order
from .forms import OrderForm, RepairForm

def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 
    
def index(request):
	"""The home page for EPR"""
	return render(request, 'mtn/index.html')

@login_required
def maint(request):
	"""The home page for Maintenance"""
	return render(request, 'mtn/maint.html')
	
@login_required
def orders(request):
	"""Show all open orders."""
	orders = Order.objects.filter(owner=request.user, closed=False).order_by('-date_added')
	context = {'orders': orders}
	return render(request, 'mtn/orders.html', context)

@login_required
def closed_orders(request):
	"""Show all closed orders."""
	orders = Order.objects.filter(owner=request.user, closed=True).order_by('-date_added')
	context = {'orders': orders}
	return render(request, 'mtn/orders.html', context)

@login_required
def order(request, id):
	"""Show a single order and all its entries."""
	if (has_group(request.user, 'maintenance') or 
		has_group(request.user, 'supervisor')):
			order = get_object_or_404(Order, id=id)
		
	else:
		raise Http404

	context = {'order': order,}
	return render(request, 'mtn/order.html', context)

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
				return HttpResponseRedirect(reverse('mtn:orders'))
	
	else:
		raise Http404		
											
	context = {'form': form}
	return render(request, 'mtn/new_order.html', context)
	
@login_required
def edit_order(request, id):
	"""Edit an existing repair."""
	if has_group(request.user, 'maintenance'):
		order = Order.objects.get(id=id)

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

@login_required
def orders_bypress(request, press_id):
	"""Show all orders for this press."""
	orders = Order.objects.filter(local=press_id).order_by('-date_added')
	context = {'orders': orders}
	return render(request, 'mtn/orders.html', context)

# def add_part(request, order_id):
# 	order = Order.objects.get(pk=order_id)
# 	PartFormset = inlineformset_factory(Order, Part, fields=('partname',), extra=1)

# 	if request.method == 'POST':
# 		formset = PartFormset(request.POST, instance=order)
# 		if formset.is_valid():
# 			formset.save
# 			return redirect('', order_id=order.id)

# formset = PartFormset(instance=order)

# return render(request, 'index.html', {'formset': formset})