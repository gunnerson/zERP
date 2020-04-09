from django.db import models

from equip.models import Press
		
class Part(models.Model):
	"""List of company equipment"""
	partnum = models.CharField(max_length=20)
	descr = models.TextField(blank=True, null=True)
	cat = models.ManyToManyField(Press)
	amount = models.PositiveIntegerField()
	unit = models.CharField(max_length=5)
	price = models.FloatField(blank=True, null=True)
	vendr = models.ManyToManyField('Vendor', blank=True)

	def __str__(self):
		return str(self.partnum)


class UsedPart(models.Model):
    """List of company equipment"""
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    amount_used = models.PositiveIntegerField()
    
    def __str__(self):
        return str(self.part)

class Vendor(models.Model):
	"""List of Vendors"""
	name = models.CharField(max_length=50)
	addr1 = models.CharField(max_length=95, blank=True, null=True)
	addr2 = models.CharField(max_length=10, blank=True, null=True)
	city = models.CharField(max_length=35, blank=True, null=True)
	state = models.CharField(max_length=2, blank=True, null=True)
	zipcode = models.CharField(max_length=10, blank=True, null=True)
	email = models.EmailField(blank=True, null=True)
	phone = models.CharField(max_length=20, blank=True, null=True)
	vcomm = models.TextField(blank=True, null=True)

	def __str__(self):
		return str(self.name)
