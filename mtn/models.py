from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.timezone import now
from django.db.models import Q
from staff.models import Employee
from equip.models import Press
from invent.models import Part


class Order(models.Model):
    """Maintenance work orders"""
    REPAIR = 'RE'
    SETUP = 'ST'
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
                              models.SET_NULL,
                              null=True,
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
    timerepidle = models.DurationField(null=True, blank=True)
    owner = models.ForeignKey(User,
                              on_delete=models.SET_NULL,
                              null=True,
                              )
    status = models.CharField(
        max_length=2,
        choices=ORDER_STATUS,
        default='SB',
    )
    closed = models.BooleanField(default=False)
    parts = models.ManyToManyField(Part, through='invent.UsedPart')

    def cost_of_repair(self):
        cost_of_repair = 0
        used_parts = self.usedpart_set.filter(marked_to_delete=False)
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


class Image(models.Model):
    """Uploaded images related to a work order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    image = models.ImageField()

    def __str__(self):
        return str(self.image.url)


class Downtime(models.Model):
    """Downtime sessions"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
