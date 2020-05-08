from django import forms
from .models import Press, Upload


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
                'placeholder': 'Describe file',
            }
            ),
        }
