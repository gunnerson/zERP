from django import forms
from .models import Order
from tempus_dominus.widgets import DatePicker


class OrderForm(forms.ModelForm):
	class Meta:
		model = Order
		fields = ['origin', 'local', 'ordertype', 'descr', ]
		labels = {'origin': 'Originator', 'local': 'Location', 
					'ordertype': 'Type','descr': 'Description', }
		widgets = {'descr': forms.Textarea(attrs={'cols': 80})}

class RepairForm(forms.ModelForm):
	timerep = forms.FloatField(min_value=0.1, max_value=99.9)
	repdate = forms.DateField(widget=DatePicker())
	class Meta:
		model = Order
		fields = ['origin', 'local', 'ordertype', 'descr', 'repdate', 
			'repby', 'cause', 'descrrep', 'timerep', 'closed']
		labels = {'origin': 'Originator', 'local': 'Location', 
					'ordertype': 'Type','descr': 'Description', 
					'repby': 'Repaired by', 'repdate': 'Repaired on', 
					'cause': 'Cause of repair', 'descrrep': 
					'Description of repair', 'timerep': 'Time of repair',
					'closed': 'Closed', }
		widgets = {
			'descrrep': forms.Textarea(attrs={'cols': 80}),
		}
