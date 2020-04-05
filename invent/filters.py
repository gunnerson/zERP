import django_filters

from .models import Part, Vendor

class PartFilter(django_filters.FilterSet):

	class Meta:
		model = Part
		fields = {
			'partnum': ['icontains'],
		}
