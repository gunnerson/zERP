import django_filters

from .models import Part, Vendor

class PartFilter(django_filters.FilterSet):
    part = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Part
        fields = {
			'partnum': ['icontains'],
		}
