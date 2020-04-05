from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Part, Vendor
from .forms import PartForm, VendorForm
from .filters import PartFilter

def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 

def PartsList(request):
	qs = Part.objects.all()
	search_part_query = request.GET.get('search_part')

	if search_part_query != '' and search_part_query is not None:
		qs = qs.filter(Q(partnum__icontains=search_part_query) 
			| Q(descr__icontains=search_part_query)
			).distinct()

	context = {	
		'queryset': qs
	}
	return render(request, "invent/partslist.html", context)
 
@login_required
def new_part(request):
	"""Add new part"""
	if has_group(request.user, 'maintenance'):
	
		if request.method != 'POST':
			# No data submitted; create a blank form.
			form = PartForm()

		else:
		# POST data submitted; process data.
			form = PartForm(data=request.POST)
			if form.is_valid():
				form.save()
				return HttpResponseRedirect(reverse('invent:partslist'))
	
	else:
		raise Http404	
								
	context = {'form': form}
	return render(request, 'invent/new_part.html', context)

@login_required
def new_vendor(request):
	"""Add new part"""
	if has_group(request.user, 'maintenance'):
	
		if request.method != 'POST':
			# No data submitted; create a blank form.
			form = VendorForm()

		else:
		# POST data submitted; process data.
			form = VendorForm(data=request.POST)
			if form.is_valid():
				form.save()
				return HttpResponseRedirect(reverse('invent:partslist'))
	
	else:
		raise Http404	
								
	context = {'form': form}
	return render(request, 'invent/new_vendor.html', context)
