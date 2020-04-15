from django.db import models
from django.urls import reverse
from django.db.models import Q

from equip.models import Press


def is_valid_param(param):
    if param == 'query':
        return param != '' and param is not None
    else:
        return (param is not None and
                param != 'Choose vendor...' and
                param != 'All vendors'
                )


class PartManager(models.Manager):
    def search(self, query=None, by_vendor=None, press=None):
        qs = self.get_queryset()
        if is_valid_param(query):
            qs = qs.filter(Q(partnum__icontains=query) |
                           Q(descr__icontains=query)
                           ).distinct()
        if is_valid_param(by_vendor):
            qs = qs.filter(vendr__name=by_vendor)
        return qs


class Part(models.Model):
    """List of inventory"""
    partnum = models.CharField(max_length=35)
    descr = models.TextField(blank=True, null=True)
    cat = models.ManyToManyField(Press)
    amount = models.PositiveIntegerField()
    unit = models.CharField(max_length=5)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    vendr = models.ManyToManyField('Vendor', blank=True)

    objects = PartManager()

    def __str__(self):
        return str(self.partnum)

    def get_absolute_url(self):
        return reverse('invent:part', kwargs={'pk': self.id})


class UsedPart(models.Model):
    """Intermediary table for m2m between Part and Order classes"""
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    order = models.ForeignKey('mtn.Order', on_delete=models.CASCADE)
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
    phone = models.CharField(max_length=20, blank=True, null=True)
    vcomm = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse('invent:vendor', kwargs={'pk': self.id})
