from django import forms
from .models import Part

class PartForm(forms.ModelForm):
	price = forms.FloatField(min_value=0, initial=0)
	amount = forms.IntegerField(min_value=0, initial=0)
	class Meta:
		model = Part
		fields = ['partnum', 'cat', 'amount', 'unit', 'addr', 'descr', 
			'vendr', 'price',
		]
		labels = {'partnum': 'Part number', 'cat': 'Category', 'amount': 
			'Amount', 'unit': 'Unit', 'addr': 'Location', 'vendr': 
			'Vendors', 'price': 'Price', 'descr': 'Description', 
		}
	initial = {'unit': 'items', }
