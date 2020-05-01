from django.db import models
from django.utils.timezone import now

from staff.models import Employee


class Bug(models.Model):
    """System bugs and suggestions"""
    origin = models.ForeignKey(Employee,
                               on_delete=models.SET_NULL,
                               null=True,
                               blank=True,
                               )
    descr = models.TextField()
    date_added = models.DateTimeField(default=now)
    metadata = models.TextField(null=True, blank=True)
