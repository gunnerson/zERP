from django.db import models
from django.urls import reverse

from mtn.cm import dbsearch, is_valid_param, is_valid_vendor


class PartManager(models.Manager):
    def search(self, query, vendor):
        qs = self.get_queryset()
        if is_valid_param(query):
            qs = dbsearch(qs, query, 'B', 'partnum', 'descr')
        if is_valid_vendor(vendor):
            qs = qs.filter(vendr__name=vendor)
        return qs


class Part(models.Model):
    """List of inventory"""
    partnum = models.CharField(blank=True, null=True, max_length=35)
    descr = models.TextField(null=True)
    cat = models.ManyToManyField('equip.Press', blank=True)
    amount = models.PositiveIntegerField()
    unit = models.CharField(max_length=5)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    vendr = models.ManyToManyField('Vendor', blank=True)

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
    order = models.ForeignKey(
        'mtn.Order', on_delete=models.CASCADE, null=True, blank=True)
    pm = models.ForeignKey(
        'mtn.Pm', on_delete=models.CASCADE, null=True, blank=True)
    amount_used = models.PositiveIntegerField()

    def __str__(self):
        return str(self.part)


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
