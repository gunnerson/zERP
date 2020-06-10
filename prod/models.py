from django.db import models
from datetime import datetime, timedelta

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
    date = models.DateTimeField(null=True)
    shift = models.IntegerField(null=True,
                                choices=((1, '1st Shift'), (0, '2nd Shift'),
                                         (2, '3rd Shift'), (3, 'SAT')))
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.job.name)

    def start_time(self):
        if self.shift == 0:
            start_time = self.date + timedelta(hours=8)
        elif self.shift == 1:
            start_time = self.date + timedelta(hours=24)
        elif self.shift == 2:
            start_time = self.date + timedelta(hours=16)
        return start_time

    def end_time(self):
        if self.shift == 0:
            end_time = self.date + timedelta(hours=16)
        elif self.shift == 1:
            end_time = self.date + timedelta(hours=32)
        elif self.shift == 2:
            end_time = self.date + timedelta(hours=24)
        return end_time
