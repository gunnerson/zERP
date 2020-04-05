import random
from django.core.management.base import BaseCommand
from invent.models import Part, Vendor

vendors = [
	'Mcmaster',
	'Grainger',
	'Amazon'
]

def generate_vendor():
	index = random.randint(0, 2)
	return vendors[index]

class Command(BaseCommand):
	
	def add_arguments(self, parser):
		parser.add_argument('file_name', type=str, 
			help='The txt file thatcontains part numbers')

	def handle(self, *args, **kwargs):
		file_name = kwargs['file_name']
		with open(f'{file_name}.txt') as file:
			for row in file:
				partnum = row
				vendr = generate_vendor()
				
				print(partnum, vendr)
