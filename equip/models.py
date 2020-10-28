import os
from django.db import models
from django.urls import reverse
from django.utils import timezone

from mtn.cm import get_shift
from invent.models import Part


class Press(models.Model):
    PRODUCTION = 'PR'
    GENERAL = 'GN'
    BUILDING = 'BD'
    LIFTING = 'LF'
    TOOLING = 'TL'
    GROUPS = [
        (PRODUCTION, 'Production'),
        (GENERAL, 'General'),
        (BUILDING, 'Building'),
        (LIFTING, 'Lifting equipment'),
        (TOOLING, 'Tooling'),
    ]
    CONVENTIONAL = 'CN'
    VACUUM = 'VC'
    INJECTION = 'IN'
    PUNCHING = 'PN'
    OTHER = 'OT'
    SUBGROUPS = [
        (CONVENTIONAL, 'Conventional'),
        (VACUUM, 'Vacuum'),
        (INJECTION, 'Injection'),
        (PUNCHING, 'Punching'),
        (OTHER, 'Other'),
    ]
    pname = models.CharField(max_length=40)
    altname = models.CharField(max_length=40, null=True, blank=True)
    group = models.CharField(
        max_length=2,
        choices=GROUPS,
    )
    subgroup = models.CharField(
        max_length=2,
        choices=SUBGROUPS,
        null=True,
        blank=True,
    )
    pmed = models.BooleanField(default=False)
    contacts = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'presses'
        ordering = ['pname']

    def __str__(self):
        return str(self.pname)

    def get_absolute_url(self):
        return reverse('equip:press', kwargs={'pk': self.id})

    def downtime(self, month, year):
        """Calculate downtime on a monthly basis"""
        dt = 0
        press = self.get_object()
        orders = press.order_set.filter(
            closed=True,
            ordertype='RE',
            date_added__year__exact=year,
            date_added__month__exact=month,
        )
        for order in orders:
            dt += order.timerep.total_seconds() / 3600
            dt += order.timerepidle.total_seconds() / 3600
        return dt

    def status(self):
        """Get press status"""
        last_order = self.order_set.filter(closed=False).first()
        if last_order is not None:
            status = last_order.get_status_display()
        else:
            status = 'Ready'
        return status

    def job(self, shift=None):
        """Get press status"""
        from prod.models import JobInst
        if shift is None:
            try:
                return self.jobinst_set.first()
            except JobInst.DoesNotExist:
                return None
        else:
            try:
                return self.jobinst_set.filter(shift=shift).first()
            except JobInst.DoesNotExist:
                return None


class Upload(models.Model):
    """Uploaded files with press documentaiton"""
    press = models.ManyToManyField(Press, blank=True)
    part = models.ManyToManyField(Part, blank=True)
    descr = models.CharField(max_length=200)
    file = models.FileField()
    uhash = models.CharField(max_length=64, null=True)

    def __str__(self):
        return str(self.descr)


class Imprint(models.Model):
    """Press drawing"""
    press = models.ForeignKey(Press, on_delete=models.CASCADE, null=True)
    x = models.IntegerField()
    y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()

    def __str__(self):
        return str(self.press.pname)


class Pmproc(models.Model):
    """PM procedure"""
    local = models.ForeignKey(Press, on_delete=models.SET_NULL,
                              null=True,
                              blank=True,
                              )
    freq = models.PositiveIntegerField(null=True)
    pm_part = models.ForeignKey(Part,
                                on_delete=models.SET_NULL,
                                null=True,
                                blank=True,
                                )
    pm_part_amount = models.PositiveIntegerField(null=True, blank=True)
    descr = models.CharField(max_length=200, null=True)
    hours = models.PositiveIntegerField(null=True)

    def hours_left(self):
        hours_left = self.freq - self.hours
        if hours_left >= 0:
            return hours_left
        else:
            return 0

    def in_stock(self):
        if self.pm_part is not None:
            if self.pm_part_amount <= self.pm_part.amount:
                return "In Stock"
            else:
                return "Out of Stock"
        else:
            return "In Stock"


class Pmsched(models.Model):
    """Scheduled PM"""
    date = models.DateField(null=True)
    local = models.ForeignKey(Press, on_delete=models.SET_NULL,
                              null=True,
                              blank=True,
                              )
    procs = models.ManyToManyField(Pmproc, blank=True)

    def __str__(self):
        return str(self.local)
        # return u", ".join([a.pname for a in self.local.all()])

    def get_absolute_url(self):
        return reverse('equip:pm-detail', kwargs={'pk': self.pk})
