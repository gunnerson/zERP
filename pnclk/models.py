from django.db import models

from staff.models import Employee


class Record(models.Model):
    """Working session"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    start = models.DateTimeField(null=True)
    lunchin = models.DateTimeField(null=True, blank=True)
    lunchout = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
