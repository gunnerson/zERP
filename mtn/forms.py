from django import forms

from .models import Order, Image
from staff.models import Employee


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['origin', 'local', 'ordertype', 'descr', 'status', ]
        labels = {'origin': 'Originator', 'local': 'Location',
                  'ordertype': 'Type', 'descr': 'Description',
                  'status': 'Status',
                  }
        widgets = {'descr': forms.Textarea(attrs={'cols': 80})}

    def __init__(self, request=None, *args, **kwargs):
        super(OrderCreateForm, self).__init__(*args, **kwargs)
        ordertype_choices = [('', '---------'), ('RE', 'Repair'),
                             ('ST', 'Setup')]
        status_choices = [('', '---------'),
                          ('DN', 'Priority 1: not operational, in production'),
                          ('SB', 'Priority 2: not in production'),
                          ('PR', 'Priority 3: operational, in production'), ]
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
        fields = ['origin', 'local', 'ordertype', 'descr',
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
        super(OrderUpdateForm, self).__init__(*args, **kwargs)
        self.fields['origin'].disabled = True
        self.fields['local'].disabled = True
        if (self.instance.ordertype == "ST" or
                self.instance.ordertype == "PM"):
            self.fields['cause'].disabled = True
        if self.instance.ordertype == "PM":
            self.fields['ordertype'].disabled = True
            self.fields['descr'].disabled = True


class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']
        labels = {'image': '',
                  }
