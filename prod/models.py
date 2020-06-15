import pytz
from django.db import models
from datetime import datetime, timedelta, tzinfo, timezone

from equip.models import Press


class Job(models.Model):
    """Production jobs"""
    press = models.ManyToManyField(Press, through='JobInst')
    name = models.CharField(max_length=8, null=True)
    rate = models.CharField(max_length=8, null=True, blank=True)

    def __str__(self):
        return str(self.name)


class JobInst(models.Model):
    """Production schedule"""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True)
    press = models.ForeignKey(Press, on_delete=models.CASCADE, null=True)
    date = models.DateField(null=True, blank=True)
    shift = models.IntegerField(null=True, blank=True,
                                choices=((1, '1st Shift'), (0, '2nd Shift'),
                                         (2, '3rd Shift'), (3, 'SAT')))
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.job.name)

    def start_time(self):
        ddate = self.date
        dtime = datetime(ddate.year, ddate.month, ddate.day).replace(
            tzinfo=timezone.utc).astimezone(tz=None)
        if self.shift == 0:
            start_time = dtime + timedelta(hours=21)
        elif self.shift == 1:
            start_time = dtime + timedelta(hours=13)
        elif self.shift == 2:
            start_time = dtime + timedelta(hours=5)
        return start_time

    def end_time(self):
        ddate = self.date
        dtime = datetime(ddate.year, ddate.month, ddate.day).replace(
            tzinfo=timezone.utc).astimezone(tz=None)
        if self.shift == 0:
            end_time = dtime + timedelta(hours=29)
        elif self.shift == 1:
            end_time = dtime + timedelta(hours=21)
        elif self.shift == 2:
            end_time = dtime + timedelta(hours=5)
        return end_time
