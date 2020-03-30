from django.shortcuts import render

from .models import Employee

def employees(request):
	"""Personnel list."""
	employees = Employee.objects.order_by('last_name')
	context = {'employees': employees}
	
	return render(request, 'staff/all.html', context)
