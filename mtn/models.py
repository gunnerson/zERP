from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.timezone import now
from django.db.models import Q
from django.utils import timezone
from datetime import date, timedelta

from staff.models import Employee
from equip.models import Press
from invent.models import Part
from mtn.cm import is_valid_param, is_empty_param


class Order(models.Model):
    REPAIR = 'RE'
    SETUP = 'ST'
    MOD = 'MD'
    PM = 'PM'
    NORMAL = 'NW'
    DAMAGE = 'DM'
    UNKNOWN = 'UN'
    DOWN = 'DN'
    STANDBY = 'SB'
    PARTS = 'AP'
    ORDER_TYPE = [
        (REPAIR, 'Repair'),
        (SETUP, 'Setup'),
        (MOD, 'Mod'),
        (PM, 'PM'),
    ]
    CAUSE_OF_REPAIR = [
        (NORMAL, 'Normal Wear'),
        (DAMAGE, 'Damage'),
        (UNKNOWN, 'Unknown'),
    ]
    ORDER_STATUS = [
        (STANDBY, 'Ready'),
        (DOWN, 'Out of order'),
        (REPAIR, 'Maintenance'),
        (PARTS, 'Awaiting parts'),
    ]
    ordertype = models.CharField(
        max_length=2,
        choices=ORDER_TYPE,
    )
    origin = models.ForeignKey(Employee,
                               on_delete=models.SET_NULL,
                               null=True,
                               limit_choices_to=Q(role='SV') | Q(role='MT'),
                               related_name='+',
                               )
    local = models.ForeignKey(Press,
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True,
                              )
    local2 = models.ForeignKey(Press,
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True,
                              related_name='local2_id'
                              )
    descr = models.TextField()
    date_added = models.DateTimeField(default=now)
    repby = models.ForeignKey(Employee,
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True,
                              limit_choices_to={'role': "MT"},
                              )
    cause = models.CharField(
        null=True,
        blank=True,
        max_length=2,
        choices=CAUSE_OF_REPAIR,
    )
    descrrep = models.TextField(null=True, blank=True)
    timerep = models.DurationField(null=True, blank=True)
    # timerepidle = models.DurationField(null=True, blank=True)
    owner = models.ForeignKey(User,
                              on_delete=models.SET_NULL,
                              null=True,
                              )
    status = models.CharField(
        max_length=2,
        choices=ORDER_STATUS,
        default='SB',
        blank=True,
    )
    closed = models.BooleanField(default=False)
    parts = models.ManyToManyField(Part, through='invent.UsedPart')

    def cost_of_repair(self):
        cost_of_repair = 0
        used_parts = self.usedpart_set.all()
        for part in used_parts:
            cost_of_part = part.amount_used * part.part.price
            cost_of_repair += cost_of_part
        return cost_of_repair

    def __str__(self):
        return str(f'{self.id:05}')

    class Meta:
        ordering = ['-id']

    def get_absolute_url(self):
        return reverse('mtn:order', kwargs={'pk': self.id})

    def idle_time(self):
        dt_sessions = self.downtime_set.all()
        idle_time = timedelta()
        if dt_sessions.exists():
            for session in dt_sessions:
                if is_empty_param(session.end):
                    session.end = timezone.now()
                count_days = session.end.day - session.start.day
                if count_days > 0:
                    start_day = session.start
                    end_day = session.end
                    for i in range(count_days):
                        next_day = start_day + timedelta(days=1)
                        next_day_weekday = next_day.weekday()
                        if next_day_weekday in range(0, 5) and next_day < end_day:
                            idle_time += timedelta(hours=16)
                            if i == count_days - 1:
                                idle_time += (end_day - next_day)
                        elif next_day_weekday in range(0, 5) and next_day >= end_day:
                            idle_time += (end_day -
                                          start_day - timedelta(hours=8))
                        start_day += timedelta(days=1)
                else:
                    idle_time += (session.end - session.start)
        return idle_time


class Image(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    press = models.ForeignKey(Press, on_delete=models.CASCADE, null=True)
    image = models.ImageField()

    def __str__(self):
        return str(self.image.url)


class Downtime(models.Model):
    REPAIR = 'RE'
    PARTS = 'AP'
    DOWN = 'DN'
    DT_TYPE = [
        (REPAIR, 'Maintenance'),
        (PARTS, 'Awaiting Parts'),
        (DOWN, 'Out of Order'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    dttype = models.CharField(max_length=2, null=True, choices=DT_TYPE,)
