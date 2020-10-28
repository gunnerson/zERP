from django import forms
from .models import Press, Upload, Pmsched, Pmproc
from tempus_dominus.widgets import DatePicker


class PressUpdateForm(forms.ModelForm):
    class Meta:
        model = Press
        fields = ['notes', 'contacts', ]
        labels = {'notes': 'Notes', 'contacts': 'Contacts',
                  }
        widgets = {
            'contacts': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Contacts',
            }
            ),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Notes, known issues...',
            }
            ),
        }


class UploadCreateForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ['descr', 'file']
        labels = {'descr': '', 'file': '',
                  }
        widgets = {
            'descr': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Give a unique file description',
            }
            ),
        }


class PmschedCreateForm(forms.ModelForm):
    class Meta:
        model = Pmsched
        fields = ['date']
        labels = {'date': 'Date', }
        widgets = {
            'date': DatePicker(),
        }


class PmprocCreateForm(forms.ModelForm):
    class Meta:
        model = Pmproc
        fields = ['descr', 'freq', 'pm_part', 'pm_part_amount']
        labels = {
            'descr': 'Description',
            'freq': 'Frequency',
            'pm_part': 'Part',
            'pm_part_amount': 'Amount',
        }
