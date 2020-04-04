from django import forms
from .models import Part

class PartForm(forms.ModelForm):
	amount = forms.IntegerField(min_value=0, initial=0)
	unit = forms.CharField(initial='items')

	class Meta:
		model = Part
		fields = ['partnum', 'cat', 'amount', 'unit', 'vendr', 'price',
			'descr'
		]
		labels = {'partnum': 'Part number', 'cat': 'Category', 'amount': 
			'Amount', 'unit': 'Unit', 'vendr': 'Vendors', 'price': 'Price', 
			'descr': 'Description', 
		}
