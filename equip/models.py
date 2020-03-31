from django.db import models

class Press(models.Model):
	"""List of company equipment"""
	pname = models.CharField(max_length=12)
	descr = models.CharField(max_length=35, blank=True)

	class Meta:
		verbose_name_plural = 'presses'

	def __str__(self):
		return str(self.pname)
