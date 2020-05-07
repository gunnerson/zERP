from django import forms
from .models import Press


class PressUpdateForm(forms.ModelForm):
    class Meta:
        model = Press
        fields = ['notes', 'contacts', ]
        labels = {'notes': 'Notes', 'contacts': 'Contacts'}
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
