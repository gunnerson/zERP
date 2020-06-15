import os
from django.db import models
from django.urls import reverse
from django.utils import timezone

from mtn.cm import get_shift


class Press(models.Model):
    PRODUCTION = 'PR'
    GENERAL = 'GN'
    BUILDING = 'BD'
    LIFTING = 'LF'
    GROUPS = [
        (PRODUCTION, 'Production'),
        (GENERAL, 'General'),
        (BUILDING, 'Building'),
        (LIFTING, 'Lifting equipment'),
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
        return dt

    def last_pm(self):
        """Last PM date"""
        orders = self.object.order_set.filter(
            closed=True,
            ordertype='PM'
        )
        if orders.exists():
            last_pm_order = orders.first()
            last_pm_date = last_pm_order.repdate
        else:
            last_pm_date = 'Never'
        return last_pm_date

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
    press = models.ForeignKey(Press, on_delete=models.CASCADE, null=True)
    descr = models.CharField(max_length=200)
    file = models.FileField()

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
