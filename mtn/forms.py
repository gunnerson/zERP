from django import forms

from .models import Entry, Repair

class EntryForm(forms.ModelForm):
	class Meta:
		model = Entry
		fields = ['origin', 'local', 'descr']
		labels = {'origin': 'Originator', 'local': 'Location', 
					'descr': 'Description', }
		widgets = {'descr': forms.Textarea(attrs={'cols': 80})}

class RepairForm(forms.ModelForm):
	timerep = forms.FloatField(min_value=0.1, max_value=99.9)
	class Meta:
		model = Repair
		fields = ['repby', 'cause', 'descrrep', 'timerep', 'closed']
		labels = {'repby': 'Repaired by', 'cause': 'Cause of repair', 
					'descrrep': 'Description', 'timerep': 'Time of repair',
					'closed': 'Closed', }
		widgets = {'descrrep': forms.Textarea(attrs={'cols': 80})}
