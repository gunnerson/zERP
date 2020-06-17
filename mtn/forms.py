from django import forms
from tempus_dominus.widgets import DatePicker

from .models import Order, Image, Pm
from staff.models import Employee
from equip.models import Press
from .cm import is_empty_param


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['origin', 'local', 'ordertype', 'descr', 'status', ]
        labels = {'origin': 'Originator', 'local': 'Location',
                  'ordertype': 'Type', 'descr': 'Description',
                  'status': 'Priority',
                  }
        widgets = {'descr': forms.Textarea(attrs={'cols': 80})}

    def __init__(self, request=None, press_id=None, *args, **kwargs):
        super(OrderCreateForm, self).__init__(*args, **kwargs)
        if press_id is not None:
            press = Press.objects.get(id=press_id)
            self.fields['local'].initial = press
        ordertype_choices = [('', '---------'), ('RE', 'Repair'),
                             ('ST', 'Setup')]
        status_choices = [('', '---------'),
                          ('DN', 'Priority 1: out of order'),
                          ('SB', 'Priority 2: operational'), ]
        try:
            origin_initial = Employee.objects.get(user=request.user)
        except Employee.DoesNotExist:
            origin_initial = None
        if origin_initial is not None:
            self.fields['origin'].initial = origin_initial
        self.fields['ordertype'].choices = ordertype_choices
        self.fields['status'].choices = status_choices
        self.fields['status'].initial = ''
        self.fields['ordertype'].initial = ''


class OrderUpdateForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['origin', 'local', 'ordertype', 'descr', 'closed',
                  'repby', 'cause', 'descrrep', 'timerep', 'status', ]
        labels = {'origin': 'Originator', 'local': 'Location',
                  'ordertype': 'Type', 'descr': 'Description',
                  'repby': 'Repaired by',
                  'cause': 'Cause of repair', 'descrrep':
                  'Description of repair', 'timerep': 'Time of repair',
                  'closed': 'Closed', 'status': 'Status', }
        widgets = {
            'descrrep': forms.Textarea(attrs={'cols': 80}),
        }

    def __init__(self, *args, **kwargs):
        self.has_dt = kwargs.pop('has_dt')
        super(OrderUpdateForm, self).__init__(*args, **kwargs)
        self.fields['origin'].disabled = True
        self.fields['local'].disabled = True
        if self.instance.ordertype == "ST":
            self.fields['cause'].disabled = True


    def clean(self):
        cleaned_data = super().clean()
        cc_timerep = cleaned_data.get("timerep")
        cc_closed = cleaned_data.get("closed")
        if cc_closed and is_empty_param(cc_timerep) and self.has_dt is False:
            cleaned_data.update({'closed': False})
            msg = forms.ValidationError(
                ('No downtime sessions clocked. Please fill-in repair time field'),
                code='invalid')
            self.add_error('timerep', msg)


class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']
        labels = {'image': '', }


class PmForm(forms.ModelForm):
    class Meta:
        model = Pm
        fields = ['local', 'pm_date', 'descr', 'closed', 'repby', 'time_required',
                  'closed', ]
        labels = {
            'local': 'Location',
            'pm_date': 'Date',
            'descr': 'Description',
            'repby': 'Performed by',
            'time_required': 'Time required',
            'closed': 'Closed',
        }
        widgets = {
            'pm_date': DatePicker(),
            'descrrep': forms.Textarea(attrs={'cols': 80}),
        }

    def __init__(self, *args, **kwargs):
        super(PmForm, self).__init__(*args, **kwargs)
        self.fields['local'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("closed"):
            if (is_empty_param(cleaned_data.get("repby")) or
                is_empty_param(cleaned_data.get("time_required")) or
                is_empty_param(cleaned_data.get("descr")) or
                    is_empty_param(cleaned_data.get("pm_date"))):
                cleaned_data.update({'closed': False})
                raise forms.ValidationError("Please fill-in all fields!")
