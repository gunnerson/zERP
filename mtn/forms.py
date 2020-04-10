from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django.db.models import Q
from .models import Order
from tempus_dominus.widgets import DatePicker

from invent.models import Part, is_valid_param



class OrderCreateForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['origin', 'local', 'ordertype', 'descr', ]
        labels = {'origin': 'Originator', 'local': 'Location',
                    'ordertype': 'Type','descr': 'Description', }
        widgets = {'descr': forms.Textarea(attrs={'cols': 80})}

    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner')
        super(OrderCreateForm, self).__init__(*args, **kwargs)

class OrderUpdateForm(forms.ModelForm):
    timerep = forms.FloatField(min_value=0.1, max_value=99.9, initial='0.1')
    repdate = forms.DateField(widget=DatePicker())
    class Meta:
        model = Order
        fields = ['origin', 'local', 'ordertype', 'descr', 'repdate',
            'repby', 'cause', 'descrrep', 'timerep', 'closed',]
        labels = {'origin': 'Originator', 'local': 'Location',
                    'ordertype': 'Type','descr': 'Description',
                    'repby': 'Repaired by', 'repdate': 'Repaired on',
                    'cause': 'Cause of repair', 'descrrep':
                    'Description of repair', 'timerep': 'Time of repair',
                    'closed': 'Closed', }
        widgets = {
            'descrrep': forms.Textarea(attrs={'cols': 80}),
        }


# class AddPartForm(forms.ModelForm):

#     class Meta:
#         model = Order
#         fields = ['parts', ]
#         labels = {'parts': "", }

#     def filter_list(self, request):
#         query = request.GET.get('query', None)
#         by_vendor = request.GET.get('by_vendor', None)

#         if is_valid_param(query) or is_valid_param(by_vendor):
#             search_results = Part.objects.search(query, by_vendor)
#             qs = sorted(search_results,
#                         key=lambda instance: instance.pk,
#                         reverse=True)
#             self.count = len(qs)
#             return qs
#         return Part.objects.all()

#     def __init__(self, *args, request=None, **kwargs):
#         super(AddPartForm, self).__init__(*args, **kwargs)
#         self.fields["parts"].widget = CheckboxSelectMultiple()
#         self.fields["parts"].queryset = self.filter_list(request)
