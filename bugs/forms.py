from django import forms

from .models import Bug


class BugCreateForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = ['origin', 'descr', ]
        labels = {'origin': 'Originator', 'descr': 'Description', }
        widgets = {'descr': forms.Textarea(attrs={'cols': 80})}
