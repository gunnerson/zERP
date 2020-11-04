import pytz
from django.db import models
from datetime import datetime, timedelta, tzinfo, timezone

from equip.models import Press


class JobInst(models.Model):
    press = models.ForeignKey(Press, on_delete=models.CASCADE, null=True)
    date = models.DateField(null=True, blank=True)
    shift = models.IntegerField(null=True, blank=True,
                                choices=((1, '1st Shift'), (2, '2nd Shift')))

    def start_time(self):
        ddate = self.date
        dtime = datetime(ddate.year, ddate.month, ddate.day).replace(
            tzinfo=timezone.utc).astimezone(tz=None)
        if self.shift == 2:
            start_time = dtime + timedelta(hours=20, minutes=30)
        elif self.shift == 1:
            start_time = dtime + timedelta(hours=12)
        return start_time

    def end_time(self):
        ddate = self.date
        dtime = datetime(ddate.year, ddate.month, ddate.day).replace(
            tzinfo=timezone.utc).astimezone(tz=None)
        if self.shift == 2:
            end_time = dtime + timedelta(hours=29)
        elif self.shift == 1:
            end_time = dtime + timedelta(hours=20, minutes=30)
        return end_time
