from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView

from .models import Part, Vendor
from .forms import PartForm, VendorForm
from .filters import PartFilter

def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 

class PartListView(ListView):
	
	model = Part
	template_name = 'invent/part_list.html'
	paginate_by = 2
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['filter'] = PartFilter(self.request.GET, queryset=self.get_queryset())
		return context		
  
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
				return HttpResponseRedirect(reverse('invent:part-list'))
	
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
				return HttpResponseRedirect(reverse('invent:part-list'))
	
	else:
		raise Http404	
								
	context = {'form': form}
	return render(request, 'invent/new_vendor.html', context)
