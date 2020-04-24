from django.db import models


class Employee(models.Model):
    """List of company personnel"""
    OPERATOR = 'OP'
    SUPERVISOR = 'SV'
    MAINTENANCE = 'MT'
    ROLES = [
        (OPERATOR, 'Operator'),
        (SUPERVISOR, 'Supervisor'),
        (MAINTENANCE, 'Maintenance'),
    ]
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20, null=True)
    role = models.CharField(
        max_length=2,
        choices=ROLES,
    )

    def __str__(self):
        if self.last_name is not None:
            return str(self.first_name) + " " + str(self.last_name)
        else:
            return str(self.first_name)
