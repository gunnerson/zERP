from django import forms

from tempus_dominus.widgets import DatePicker

from .models import Order, Image


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['local', 'ordertype', 'descr', 'status', ]
        labels = {'local': 'Location',
                  'ordertype': 'Type', 'descr': 'Description',
                  'status': 'Status',
                  }
        widgets = {'descr': forms.Textarea(attrs={'cols': 80})}

    def __init__(self, *args, **kwargs):
        super(OrderCreateForm, self).__init__(*args, **kwargs)
        ordertype_choices = [('RE', 'Repair'), ('ST', 'Setup'), ]
        status_choices = [('DN', 'Out of order'), ('SB', 'Stand-by'),
                          ('PR', 'Production'), ]
        self.fields['ordertype'].choices = ordertype_choices
        self.fields['status'].choices = status_choices
        self.fields['status'].initial = ''


class OrderUpdateForm(forms.ModelForm):
    repdate = forms.DateField(widget=DatePicker(), required=False,
                              label="Date of repair")

    class Meta:
        model = Order
        fields = ['owner', 'local', 'ordertype', 'descr', 'repdate',
                  'repby', 'cause', 'descrrep', 'timerep', 'status', ]
        labels = {'owner': 'Originator', 'local': 'Location',
                  'ordertype': 'Type', 'descr': 'Description',
                  'repby': 'Repaired by', 'repdate': 'Repair date',
                  'cause': 'Cause of repair', 'descrrep':
                  'Description of repair', 'timerep': 'Time of repair',
                  'closed': 'Closed', 'status': 'Status', }
        widgets = {
            'descrrep': forms.Textarea(attrs={'cols': 80}),
        }

    def __init__(self, *args, **kwargs):
        super(OrderUpdateForm, self).__init__(*args, **kwargs)
        self.fields['owner'].disabled = True
        if (self.instance.ordertype == "ST" or
                self.instance.ordertype == "PM"):
            self.fields['cause'].disabled = True
        if self.instance.ordertype == "PM":
            self.fields['local'].disabled = True
            self.fields['owner'].disabled = True
            self.fields['ordertype'].disabled = True
            self.fields['descr'].disabled = True


class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']
        labels = {'image': '',
                  }
