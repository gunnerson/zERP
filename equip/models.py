import os
from django.db import models
from django.urls import reverse


class Press(models.Model):
    pname = models.CharField(max_length=40)
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
            last_pm_order = orders.last()
            last_pm_date = last_pm_order.repdate
        else:
            last_pm_date = 'Never'
        return last_pm_date


class Upload(models.Model):
    """Uploaded files with press documentaiton"""
    press = models.ForeignKey(Press, on_delete=models.CASCADE, null=True)
    descr = models.CharField(max_length=200)
    file = models.FileField()

    def __str__(self):
        return str(self.descr)
