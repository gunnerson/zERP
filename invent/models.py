from django.db import models
from django.urls import reverse
# from django.db.models import Q
from django.contrib.postgres.search import SearchVectorField, SearchQuery, SearchRank, SearchVector

from equip.models import Press


def is_valid_vendor(param):
    return (param is not None and
            param != 'Choose vendor...' and
            param != 'All vendors'
            )


def is_valid_queryparam(param):
    return param != '' and param is not None


class PartManager(models.Manager):
    def search(self, query, by_vendor):
        qs = self.get_queryset()
        if is_valid_queryparam(query):
            query = SearchQuery(query)
            vector = SearchVector('textsearchable_index_col')
            qs = qs.annotate(rank=SearchRank(vector, query)).filter(
                textsearchable_index_col=query).order_by('-rank')
        if is_valid_vendor(by_vendor):
            qs = qs.filter(vendr__name=by_vendor)
        return qs


class Part(models.Model):
    """List of inventory"""
    partnum = models.CharField(max_length=35)
    descr = models.TextField(blank=True, null=True)
    cat = models.ManyToManyField(Press, blank=True)
    amount = models.PositiveIntegerField()
    unit = models.CharField(max_length=5)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    vendr = models.ManyToManyField('Vendor', blank=True)
    textsearchable_index_col = SearchVectorField(null=True)

    objects = PartManager()

    class Meta:
        ordering = ['partnum']

    def __str__(self):
        return str(self.partnum)

    def get_absolute_url(self):
        return reverse('invent:part', kwargs={'pk': self.id})


class UsedPart(models.Model):
    """Intermediary table for m2m between Part and Order classes"""
    part = models.ForeignKey(Part, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey('mtn.Order', on_delete=models.CASCADE, null=True)
    amount_used = models.PositiveIntegerField()
    marked_to_delete = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Vendor(models.Model):
    """List of Vendors"""
    name = models.CharField(max_length=50)
    addr1 = models.CharField(max_length=95, blank=True, null=True)
    addr2 = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=35, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    webpage = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    vcomm = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse('invent:vendor', kwargs={'pk': self.id})

# Create indexes:
# ALTER TABLE invent_part
#     ADD COLUMN textsearchable_index_col tsvector
#                GENERATED ALWAYS AS (to_tsvector('english', coalesce(partnum, '') || ' ' || coalesce(descr, ''))) STORED;
# CREATE INDEX partsearch_idx ON invent_part USING GIN (textsearchable_index_col);
