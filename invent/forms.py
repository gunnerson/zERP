from django import forms
from .models import Part

class PartForm(forms.ModelForm):
	price = forms.FloatField(min_value=0, initial=0)		
	class Meta:
		model = Part
		fields = ['partnum', 'cat', 'amount', 'quant', 'addr', 'descr', 
			'vendor', 'venci', 'price',
		]
		labels = {'partnum': 'Part number', 'cat': 'Category', 'amount': 
			'Amount', 'quant': 'Quantity', 'addr': 'Location', 'vendor': 
			'Vendor', 'venci': 'Vendor Contact Information', 'price': 'Price',
			'descr': 'Description', 
		}
	
