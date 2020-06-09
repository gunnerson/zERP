from django.db import models

from equip.models import Press


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
