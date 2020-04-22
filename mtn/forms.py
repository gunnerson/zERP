from django import forms

from tempus_dominus.widgets import DatePicker

from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['origin', 'local', 'ordertype', 'descr', ]
        labels = {'origin': 'Originator', 'local': 'Location',
                  'ordertype': 'Type', 'descr': 'Description', }
        widgets = {'descr': forms.Textarea(attrs={'cols': 80})}


class OrderUpdateForm(forms.ModelForm):
    timerep = forms.FloatField(min_value=0, max_value=99.9, initial=0,
                               label="Time of repair, h")
    repdate = forms.DateField(widget=DatePicker(), required=False,
                              label="Date of repair, h")

    class Meta:
        model = Order
        fields = ['origin', 'local', 'ordertype', 'descr', 'repdate',
                  'repby', 'cause', 'descrrep', 'timerep', 'closed', ]
        labels = {'origin': 'Originator', 'local': 'Location',
                  'ordertype': 'Type', 'descr': 'Description',
                  'repby': 'Repaired by', 'repdate': 'Repaired on',
                  'cause': 'Cause of repair', 'descrrep':
                  'Description of repair', 'timerep': 'Time of repair',
                  'closed': 'Closed', }
        widgets = {
            'descrrep': forms.Textarea(attrs={'cols': 80}),
        }

    def __init__(self, *args, **kwargs):
        super(OrderUpdateForm, self).__init__(*args, **kwargs)
        if (self.instance.ordertype == "ST" or
                self.instance.ordertype == "PM"):
            self.fields['cause'].disabled = True

    # def __init__(self, *args, request=None, **kwargs):
    #     super(OrderUpdateForm, self).__init__(*args, **kwargs)
    #     self.fields["parts"].widget = CheckboxSelectMultiple()
    #     self.fields["parts"].queryset = self.filter_list(request)
