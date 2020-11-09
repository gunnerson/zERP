from django import forms
from tempus_dominus.widgets import DatePicker

from .models import Order, Image, Downtime
from staff.models import Employee
from equip.models import Press
from .cm import is_empty_param, is_valid_param


class OrderCreateForm(forms.ModelForm):
    mold = forms.CharField(required=False)

    class Meta:
        model = Order
        fields = ['origin', 'local', 'ordertype', 'descr', 'status', ]
        labels = {
            'origin': 'Originator',
            'local': 'Location',
            'ordertype': 'Type',
            'descr': 'Description',
            'status': 'Status',
        }
        widgets = {'descr': forms.Textarea(attrs={'cols': 80})}

    def __init__(self, request=None, press_id=None, *args, **kwargs):
        super(OrderCreateForm, self).__init__(*args, **kwargs)
        if press_id is not None:
            press = Press.objects.get(id=press_id)
            self.fields['local'].initial = press
        status_choices = [('', '---------'),
                          ('DN', 'OUT OF ORDER'),
                          ('SB', 'OPERATING'), ]
        self.fields['status'].choices = status_choices
        self.fields['status'].initial = ''
        try:
            self.fields['origin'].initial = Employee.objects.get(
                user=request.user)
        except Employee.DoesNotExist:
            pass

    def clean(self):
        cleaned_data = super().clean()
        cc_local = cleaned_data.get("local")
        cc_mold = cleaned_data.get("mold")
        cc_status = cleaned_data.get("status")
        if is_empty_param(cc_local) and is_empty_param(cc_mold):
            msg1 = forms.ValidationError(
                ('Select location!'),
                code='invalid')
            msg2 = forms.ValidationError(
                ('Fill-in mold number!'),
                code='invalid')
            self.add_error('local', msg1)
            self.add_error('mold', msg2)
        if is_empty_param(cc_status):
            msg = forms.ValidationError(
                ('Select priority!'),
                code='invalid')
            self.add_error('status', msg)


class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['origin', 'local', 'ordertype', 'descr', 'closed',
                  'repby', 'cause', 'descrrep', 'timerep', ]
        labels = {
            'origin': 'Originator',
            'local': 'Location',
            'ordertype': 'Type',
            'descr': 'Description',
            'repby': 'Repaired by',
            'mold': 'Mold',
            'cause': 'Cause of repair',
            'descrrep': 'Description of repair',
            'timerep': 'Time of repair',
            'closed': 'Closed',
        }
        widgets = {
            'descrrep': forms.Textarea(attrs={'cols': 80}),
        }

    def __init__(self, *args, **kwargs):
        self.has_dt = kwargs.pop('has_dt')
        self.has_re_dt = kwargs.pop('has_re_dt')
        super(OrderUpdateForm, self).__init__(*args, **kwargs)
        self.fields['origin'].disabled = True
        self.fields['local'].disabled = True
        if self.has_dt:
            self.fields['timerep'].disabled = True
        if self.instance.ordertype in ("ST", "MD"):
            self.fields['cause'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        cc_timerep = cleaned_data.get("timerep")
        cc_closed = cleaned_data.get("closed")
        if cc_closed and is_empty_param(cc_timerep) and self.has_re_dt is False \
                and self.has_dt is False:
            cleaned_data.update({'closed': False})
            msg = forms.ValidationError(
                ('No repair downtime sessions clocked. Please fill-in!'),
                code='invalid')
            self.add_error('timerep', msg)


class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']
        labels = {'image': '', }


# class PmForm(forms.ModelForm):
#     class Meta:
#         model = Pm
#         fields = ['local', 'pm_date', 'descr', 'closed', 'repby', 'time_required',
#                   'closed', ]
#         labels = {
#             'local': 'Location',
#             'pm_date': 'Date',
#             'descr': 'Description',
#             'repby': 'Performed by',
#             'time_required': 'Time required',
#             'closed': 'Closed',
#         }
#         widgets = {
#             'pm_date': DatePicker(),
#             'descrrep': forms.Textarea(attrs={'cols': 80}),
#         }

#     def __init__(self, *args, **kwargs):
#         super(PmForm, self).__init__(*args, **kwargs)
#         self.fields['local'].disabled = True

#     def clean(self):
#         cleaned_data = super().clean()
#         if cleaned_data.get("closed"):
#             if (is_empty_param(cleaned_data.get("repby")) or
#                 is_empty_param(cleaned_data.get("time_required")) or
#                 is_empty_param(cleaned_data.get("descr")) or
#                     is_empty_param(cleaned_data.get("pm_date"))):
#                 cleaned_data.update({'closed': False})
#                 raise forms.ValidationError("Please fill-in all fields!")


class DowntimeForm(forms.ModelForm):
    class Meta:
        model = Downtime
        fields = ['dttype', 'start', 'end']

    def __init__(self, *args, **kwargs):
        super(DowntimeForm, self).__init__(*args, **kwargs)
        self.fields['end'].required = False

    def clean(self):
        cleaned_data = super().clean()
        cc_start = cleaned_data.get("start")
        cc_end = cleaned_data.get("end")
        if is_valid_param(cc_end) and cc_end < cc_start:
            msg = forms.ValidationError(
                ('End time must exceed start time!'),
                code='invalid')
            self.add_error('end', msg)
