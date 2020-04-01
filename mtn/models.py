from django.db import models
from django.contrib.auth.models import User

from staff.models import Employee
from equip.models import Press

class Order(models.Model):
	"""Maintenance work orders"""
	REPAIR = 'RE'
	SETUP = 'ST'
	PM = 'PM'
	ORDER_TYPE = [
		(REPAIR, 'Repair'),
		(SETUP, 'Setup'),
		(PM, 'PM'),
	]
	ordertype = models.CharField(
		max_length=2,
		choices=ORDER_TYPE,
	)
	date_added = models.DateTimeField(auto_now_add=True)
	owner = models.ForeignKey(User,on_delete=models.CASCADE)
	
	entry_filled = models.BooleanField(default=False)
	repair_filled = models.BooleanField(default=False)
	closed = models.BooleanField(default=False)

	def __str__(self):
		"""return a string representation of the model."""
		return str(self.id)

class Entry(models.Model):
	order = models.ForeignKey(Order,on_delete=models.CASCADE)
	won = models.IntegerField()
	origin = models.ForeignKey(Employee,
		on_delete=models.SET_NULL,
		null=True,
		limit_choices_to={'role': "SV"},
	)
	local =  models.ForeignKey(Press,
		models.SET_NULL,
		null=True,		
	)
	descr = models.TextField()
	date_added = models.DateField(auto_now_add=True)
		
	class Meta:
		verbose_name_plural = 'entries'
		
	def __str__(self):
		return str(self.descr)[:50] +"..."

class Repair(models.Model):	
	NORMAL = 'NW'
	DAMAGE = 'DM'
	UNKNOWN = 'UN'
	CAUSE_OF_REPAIR = [
		(NORMAL, 'Normal Wear'),
		(DAMAGE, 'Damage'),
		(UNKNOWN, 'Unknown'),
	]
	order = models.ForeignKey(Order,on_delete=models.CASCADE)
	won = models.IntegerField()
	repby = models.ForeignKey(Employee,
		on_delete=models.SET_NULL,
		null=True,
		limit_choices_to={'role': "MT"},
	)
	cause =  models.CharField(
		max_length=2,
		choices=CAUSE_OF_REPAIR,
	)
	descrrep = models.TextField()
	timerep = models.FloatField(blank=True)
	date_added = models.DateField(auto_now_add=True)
	closed = models.BooleanField(default=False)
		
	def __str__(self):
		return str(self.descrrep)[:50] +"..."
