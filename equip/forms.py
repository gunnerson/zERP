from django import forms
from .models import Press, Upload, Pmsched, Pmproc
from tempus_dominus.widgets import DatePicker


class PressCreateForm(forms.ModelForm):
    class Meta:
        model = Press
        fields = ['pname', 'group', 'subgroup', 'pmed', ]
        labels = {'pname': 'Name',
                  'group': 'Group',
                  'subgroup': 'Subgroup',
                  'pmed': 'Track PM',
                  }


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

    def clean(self):
        cleaned_data = super().clean()
        cc_descr = cleaned_data.get("descr")
        cc_part = cleaned_data.get("pm_part")
        cc_pm_part_amount = cleaned_data.get("pm_part_amount")
        if cc_part is not None and cc_pm_part_amount is None:
            msg = forms.ValidationError(
                ('Select amount!'),
                code='invalid')
            self.add_error('pm_part_amount', msg)
        if cc_descr is None:
            msg = forms.ValidationError(
                ('Fill-in description!'),
                code='invalid')
            self.add_error('descr', msg)


class PmprocUpdateForm(forms.ModelForm):
    class Meta:
        model = Pmproc
        fields = ['descr', 'freq', 'pm_part', 'pm_part_amount', 'hours']
        labels = {
            'descr': 'Description',
            'freq': 'Frequency',
            'pm_part': 'Part',
            'pm_part_amount': 'Amount',
            'hours': 'Hours',
        }

    def clean(self):
        cleaned_data = super().clean()
        cc_part = cleaned_data.get("pm_part")
        cc_pm_part_amount = cleaned_data.get("pm_part_amount")
        if cc_part is not None and cc_pm_part_amount is None:
            msg = forms.ValidationError(
                ('Select amount!'),
                code='invalid')
            self.add_error('pm_part_amount', msg)
