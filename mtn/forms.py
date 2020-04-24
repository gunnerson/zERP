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

    def __init__(self, *args, **kwargs):
        super(OrderCreateForm, self).__init__(*args, **kwargs)
        limited_choices = [('RE', 'Repair'), ('ST', 'Setup'), ]
        self.fields['ordertype'].choices = limited_choices


class OrderUpdateForm(forms.ModelForm):
    repdate = forms.DateField(widget=DatePicker(), required=False,
                              label="Date of repair")

    class Meta:
        model = Order
        fields = ['origin', 'local', 'ordertype', 'descr', 'repdate',
                  'repby', 'cause', 'descrrep', 'timerep', 'closed', ]
        labels = {'origin': 'Originator', 'local': 'Location',
                  'ordertype': 'Type', 'descr': 'Description',
                  'repby': 'Repaired by', 'repdate': 'Repair date',
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
        if self.instance.ordertype == "PM":
            self.fields['local'].disabled = True
            self.fields['origin'].disabled = True
            self.fields['ordertype'].disabled = True
            self.fields['descr'].disabled = True

    # def __init__(self, *args, request=None, **kwargs):
    #     super(OrderUpdateForm, self).__init__(*args, **kwargs)
    #     self.fields["parts"].widget = CheckboxSelectMultiple()
