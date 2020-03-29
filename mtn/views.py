from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Order, Entry, Repair
from .forms import OrderForm, EntryForm, RepairForm

def index(request):
	"""The home page for EPR"""
	return render(request, 'mtn/index.html')

def maint(request):
	"""The home page for Maintenance"""
	return render(request, 'mtn/maint.html')
	
@login_required
def orders(request):
	"""Show all open orders."""
	orders = Order.objects.filter(owner=request.user, closed=False).order_by('date_added')
	context = {'orders': orders}
	return render(request, 'mtn/orders.html', context)

@login_required
def closed_orders(request):
	"""Show all closed orders."""
	orders = Order.objects.filter(owner=request.user, closed=True).order_by('date_added')
	context = {'orders': orders}
	return render(request, 'mtn/closed_orders.html', context)

@login_required
def order(request, order_id):
	"""Show a single order and all its entries."""
	order = get_object_or_404(Order, id=order_id)
	# Make sure the topic belongs to the current user.
	if order.owner != request.user:
		raise Http404
		
	entries = order.entry_set.order_by('-date_added')
	repairs = order.repair_set.order_by('-date_added')
	context = {'order': order, 'entries': entries, 'repairs': repairs}
	return render(request, 'mtn/order.html', context)

@login_required
def new_order(request):
	"""Add new order"""
	if request.method != 'POST':
		# No data submitted; create a blank form.
		form = OrderForm()
	else:
		# POST data submitted; process data.
		form = OrderForm(request.POST)
		if form.is_valid():
			new_order = form.save(commit=False)
			new_order.owner = request.user
			new_order.save()
			form.save()
			return HttpResponseRedirect(reverse('mtn:orders'))
			
	context = {'form': form}
	return render(request, 'mtn/new_order.html', context)
	
@login_required
def new_entry(request, order_id):
	"""Add a new entry for a particular order."""
	order = Order.objects.get(id=order_id)
	if order.entry_filled:
		raise Http404
	
	if request.method != 'POST':
		# No data submitted; create a blank form.
		form = EntryForm()
	else:
	# POST data submitted; process data.
		form = EntryForm(data=request.POST)
		if form.is_valid():
			new_entry = form.save(commit=False)
			new_entry.order = order
			new_entry.won = order_id
			order.entry_filled = True
			order.save(update_fields=['entry_filled'])
			new_entry.save()			
			return HttpResponseRedirect(reverse('mtn:order',
										args=[order_id]))
										
	context = {'order': order, 'form': form}
	return render(request, 'mtn/new_entry.html', context)
	
@login_required
def edit_entry(request, entry_id):
	"""Edit an existing entry."""
	entry = Entry.objects.get(won=entry_id)
	order = entry.order
	if order.owner != request.user:
		raise Http404

	if request.method != 'POST':
		# Initial request; pre-fill form with the current entry.
		form = EntryForm(instance=entry)
	else:
		# POST data submitted; process data.
		form = EntryForm(instance=entry, data=request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('mtn:order',
												args=[order.id]))
	context = {'entry': entry, 'order': order, 'form': form}
	return render(request, 'mtn/edit_entry.html', context)	

@login_required
def new_repair(request, order_id):
	"""Add a new repair for a particular order."""
	order = Order.objects.get(id=order_id)
	if order.repair_filled:
		raise Http404
	
	if request.method != 'POST':
		# No data submitted; create a blank form.
		form = RepairForm()
	else:
	# POST data submitted; process data.
		form = RepairForm(data=request.POST)
		if form.is_valid():
			new_repair = form.save(commit=False)
			new_repair.order = order
			new_repair.won = order_id
			order.repair_filled = True
			order.closed = new_repair.closed
			order.save(update_fields=['repair_filled', 'closed'])
			new_repair.save()			
			return HttpResponseRedirect(reverse('mtn:order',
										args=[order_id]))
										
	context = {'order': order, 'form': form}
	return render(request, 'mtn/new_repair.html', context)
	
@login_required
def edit_repair(request, repair_id):
	"""Edit an existing repair."""
	repair = Repair.objects.get(won=repair_id)
	order = repair.order
	if order.owner != request.user:
		raise Http404

	if request.method != 'POST':
		# Initial request; pre-fill form with the current repair.
		form = RepairForm(instance=repair)
	else:
		# POST data submitted; process data.
		form = RepairForm(instance=repair, data=request.POST)
		if form.is_valid():
			form.save()
			order.closed = repair.closed
			order.save(update_fields=['repair_filled', 'closed'])
			return HttpResponseRedirect(reverse('mtn:order',
												args=[order.id]))
	context = {'repair': repair, 'order': order, 'form': form}
	return render(request, 'mtn/edit_repair.html', context)	
