from django import forms
from .models import Part, Vendor


class PartCreateForm(forms.ModelForm):
    amount = forms.IntegerField(min_value=0, initial=0)
    price = forms.DecimalField(min_value=0, initial=0, label='Price, $')
    unit = forms.CharField(initial='items')

    class Meta:
        model = Part
        fields = ['partnum', 'cat', 'amount', 'unit', 'vendr', 'price',
                  'descr'
                  ]
        labels = {'partnum': 'Part number', 'cat': 'Category', 'amount':
                  'Amount', 'unit': 'Unit', 'vendr': 'Vendors',
                  'price': 'Price', 'descr': 'Description',
                  }
        widgets = {
            'cat': forms.SelectMultiple(attrs={
                'size': '20',
            }
            ),
            'vendr': forms.SelectMultiple(attrs={
                'size': '20',
            }
            ),
            'descr': forms.Textarea(attrs={
                'rows': '12',
            }
            ),
        }


class VendorCreateForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'addr1', 'addr2', 'city', 'state', 'zipcode',
                  'email', 'phone', 'vcomm', 'webpage',
                  ]
        labels = {'name': 'Name', 'addr1': 'Address', 'addr2':
                  'Address (line 2)', 'city': 'City', 'state': 'State',
                  'zipcode': 'Zip Code', 'email': 'E-Mail',
                  'phone': 'Phone number', 'vcomm': 'Commentary',
                  'webpage': 'Web address',
                  }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company name',
            }
            ),
            'addr1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Address',
            }
            ),
            'addr2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Address 2',
            }
            ),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City',
            }
            ),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State',
            }
            ),
            'zipcode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Zip',
            }
            ),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone',
            }
            ),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email',
            }
            ),
            'vcomm': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Commentary',
            }
            ),
            'webpage': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Web address',
            }
            ),
        }
