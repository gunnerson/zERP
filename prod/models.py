from django.db import models

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
    date = models.DateField(null=True)
    shift = models.IntegerField(null=True,
                                choices=((1, '1st Shift'), (0, '2nd Shift'),
                                         (2, '3rd Shift'), (3, 'SAT')))
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.job.name)
