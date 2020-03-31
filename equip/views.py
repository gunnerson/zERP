from django.shortcuts import render

from .models import Press

def equip(request):
	"""Equipment list."""
	presses = Press.objects.order_by('pname')
	context = {'presses': presses}
	
	return render(request, 'equip/all.html', context)
