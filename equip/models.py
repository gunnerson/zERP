import os
from django.db import models
from django.urls import reverse
from django.utils import timezone


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
            last_pm_order = orders.first()
            last_pm_date = last_pm_order.repdate
        else:
            last_pm_date = 'Never'
        return last_pm_date

    def status(self):
        """Get press status"""
        last_order = self.order_set.first()
        if last_order is not None:
            status = last_order.get_status_display()
        else:
            status = 'Ready'
        return status

    def job(self):
        """Get press status"""
        job = ''
        last_job = self.job_set.first()
        if last_job is not None:
            if last_job.date == timezone.now().date():
                job = last_job.name
        return job


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


class Job(models.Model):
    """Production jobs"""
    press = models.ManyToManyField(Press, through='JobInst')
    name = models.CharField(max_length=8, null=True)
    rate = models.FloatField(null=True, blank=True)

    def __str__(self):
        return str(self.name)


class JobInst(models.Model):
    """Production schedule"""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True)
    press = models.ForeignKey(Press, on_delete=models.CASCADE, null=True)
    date = models.DateField(null=True)
    shift = models.CharField(max_length=1,
                             choices=(('1', '1st'), ('2', '2nd'), ('3', '3rd')),
                             null=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.job.name)
