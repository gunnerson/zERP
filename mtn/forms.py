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
	class Meta:
		model = Repair
		fields = ['repby', 'cause', 'descrrep', 'timerep', 'closed']
		labels = {'repby': 'Repaired by', 'cause': 'Cause of repair', 
					'descrrep': 'Description', 'timerep': 'Time of repair',
					'closed': 'Closed', }
		widgets = {'descrrep': forms.Textarea(attrs={'cols': 80})}
