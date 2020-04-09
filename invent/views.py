from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Part, Vendor
from .forms import PartForm, VendorForm


def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 
    

def is_valid_queryparam(param):
	return param != '' and param is not None


def PartsList(request):
	qs = Part.objects.all()
	search_part_query = request.GET.get('search_part')
	by_vendor = request.GET.get('by_vendor')
	vendors = Vendor.objects.exclude(name__exact=by_vendor)

	if is_valid_queryparam(search_part_query):
		qs = qs.filter(Q(partnum__icontains=search_part_query) 
			| Q(descr__icontains=search_part_query)
			).distinct()

	if (is_valid_queryparam(by_vendor) and by_vendor != 'Choose vendor...' 
		and by_vendor != 'All vendors'):
		qs = qs.filter(vendr__name=by_vendor)

	context = {	
		'queryset': qs,
		'vendors': vendors,
		'search_part_query': search_part_query,
		'by_vendor': by_vendor
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
