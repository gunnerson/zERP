from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.timezone import now

from staff.models import Employee
from equip.models import Press
from invent.models import Part


class Order(models.Model):
    """Maintenance work orders"""
    REPAIR = 'RE'
    SETUP = 'ST'
    NORMAL = 'NW'
    DAMAGE = 'DM'
    UNKNOWN = 'UN'
    ORDER_TYPE = [
        (REPAIR, 'Repair'),
    ]
    CAUSE_OF_REPAIR = [
        (NORMAL, 'Normal Wear'),
        (DAMAGE, 'Damage'),
        (UNKNOWN, 'Unknown'),
    ]
    ordertype = models.CharField(
        max_length=2,
        choices=ORDER_TYPE,
    )
    origin = models.ForeignKey(Employee,
                               on_delete=models.SET_NULL,
                               null=True,
                               limit_choices_to={'role': "SV"},
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
                              limit_choices_to={'role': "MT"},
                              )
    cause = models.CharField(
        null=True,
        blank=True,
        max_length=2,
        choices=CAUSE_OF_REPAIR,
    )
    descrrep = models.TextField(null=True)
    timerep = models.DurationField(null=True, blank=True)
    repdate = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(User,
                              on_delete=models.SET_NULL,
                              null=True,
                              )
    closed = models.BooleanField(default=False)
    parts = models.ManyToManyField(Part, through='invent.UsedPart')

    def cost_of_repair(self):
        cost_of_repair = 0
        used_parts = self.object.usedpart_set.filter(marked_to_delete=False)
        for part in used_parts:
            cost_of_part = part.amount_used * part.part.price
            cost_of_repair += cost_of_part
        return cost_of_repair

    def __str__(self):
        return str(f'{self.id:05}')

    def get_absolute_url(self):
        return reverse('mtn:order', kwargs={'pk': self.id})
