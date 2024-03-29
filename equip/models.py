# import os
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q

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
    joined = models.OneToOneField('self',
                                  on_delete=models.CASCADE,
                                  null=True,
                                  blank=True,)
    primary = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'presses'
        ordering = ['pname']

    def __str__(self):
        return str(self.pname)

    def get_absolute_url(self):
        return reverse('equip:press', kwargs={'pk': self.id})

    def downtime(self, month, year):
        dt = 0
        press = self.get_object()
        # orders = press.order_set.filter(
        #     closed=True,
        #     ordertype='RE',
        #     date_added__year__exact=year,
        #     date_added__month__exact=month,
        # )
        from mtn.models import Order
        orders = Order.objects.filter(
            Q(local=press) | Q(local2=press),
            closed=True,
            ordertype='RE',
            date_added__year__exact=year,
            date_added__month__exact=month,
        )
        for order in orders:
            dt += order.timerep.total_seconds() / 3600
            # dt += order.timerepidle.total_seconds() / 3600
        return dt

    def prod_hours(self, month, year):
        ph = int(0)
        press = self.get_object()
        shifts = press.jobinst_set.filter(
            date__year__exact=year,
            date__month__exact=month,
        )
        for shift in shifts:
            ph += 8
        return ph

    def status(self):
        last_order = self.order_set.filter(closed=False).first()
        if last_order is not None:
            status = last_order.get_status_display()
        else:
            status = 'Ready'
        return status

    def last_pm(self):
        qs = self.pmsched_set.all().order_by('date')
        last_pm = qs.last()
        if last_pm is not None:
            last_pm_date = last_pm.date
        else:
            last_pm_date = None
        return last_pm_date

    def pm_due(self):
        procs = self.pmproc_set.all()
        pm_due = False
        i = 0
        while not pm_due and i < procs.count():
            if procs[i].hours >= procs[i].freq:
                pm_due = True
            i += 1
        return pm_due

    def pm_prior(self):
        today = timezone.now().date()
        if self.last_pm() is not None:
            pm_prior = today - self.last_pm()
            return int(pm_prior.days)
        else:
            return 0

    def job(self, shift=get_shift()):
        from prod.models import JobInst
        try:
            return self.jobinst_set.get(shift=shift, date=timezone.now().date())
        except JobInst.DoesNotExist:
            pass

    def pm_today(self):
        if self.last_pm() == timezone.now().date():
            return True
        else:
            return False


class Upload(models.Model):
    press = models.ManyToManyField(Press, blank=True)
    part = models.ManyToManyField(Part, blank=True)
    descr = models.CharField(max_length=200)
    file = models.FileField()
    uhash = models.CharField(max_length=64, null=True)

    def __str__(self):
        return str(self.descr)


class Imprint(models.Model):
    press = models.ForeignKey(Press, on_delete=models.CASCADE, null=True)
    x = models.IntegerField()
    y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()

    def __str__(self):
        return str(self.press.pname)


class Pmproc(models.Model):
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
    descr = models.CharField(max_length=200, null=True, blank=True)
    hours = models.PositiveIntegerField(null=True)

    def hours_left(self):
        hours_left = self.freq - self.hours
        if hours_left >= 0:
            return hours_left
        else:
            return 0

    def get_admin_url(self):
        info = (self._meta.app_label, self._meta.model_name)
        admin_url = reverse('admin:%s_%s_change' % info, args=(self.pk,))
        return admin_url

    def in_stock(self):
        if self.pm_part is not None:
            if self.pm_part_amount <= self.pm_part.amount:
                return "In Stock"
            else:
                return "Out of Stock"
        else:
            return "In Stock"


class Pmsched(models.Model):
    date = models.DateField(null=True)
    local = models.ForeignKey(Press, on_delete=models.SET_NULL,
                              null=True,
                              blank=True,
                              )

    def __str__(self):
        return str(self.local)
        # return u", ".join([a.pname for a in self.local.all()])

    def get_absolute_url(self):
        return reverse('equip:pm-detail', kwargs={'pk': self.pk})
