from django.db import models
from django.contrib.auth.models import User

from staff.models import Employee

class Order(models.Model):
	"""Maintenance work orders"""
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
	origin = models.ForeignKey(Employee,on_delete=models.CASCADE)
	local =  models.CharField(max_length=200)
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
	repby = models.ForeignKey(Employee,on_delete=models.CASCADE)
	cause =  models.CharField(
		max_length=2,
		choices=CAUSE_OF_REPAIR,
		default=UNKNOWN,
	)
	descrrep = models.TextField()
	timerep = models.CharField(max_length=4)
	date_added = models.DateField(auto_now_add=True)
	closed = models.BooleanField(default=False)
		
	def __str__(self):
		return str(self.descrrep)[:50] +"..."
