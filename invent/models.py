from django.db import models

from equip.models import Press

class Part(models.Model):
	"""List of company equipment"""
	partnum = models.CharField(max_length=20, blank=True, null=True)
	descr = models.TextField(blank=True, null=True)
	cat = models.ManyToManyField(Press)
	amount = models.PositiveIntegerField()
	quant = models.CharField(max_length=4)
	price = models.FloatField(blank=True, null=True)
	vendor = models.CharField(max_length=20, blank=True, null=True)
	venci = models.CharField(max_length=35, blank=True, null=True)
	addr = models.CharField(max_length=20, blank=True, null=True)
	
	def __str__(self):
		return str(self.id)
