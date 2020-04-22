from django.db import models


class Press(models.Model):
    REPAIR = 'RE'
    SETUP = 'ST'
    PM = 'PM'
    OK = 'OK'
    PRESS_STATUS = [
        (REPAIR, 'Out of Order'),
        (SETUP, 'Setup Due'),
        (PM, 'PM Due'),
        (OK, 'OK'),
    ]
    pname = models.CharField(max_length=12)
    status = models.CharField(
        max_length=2,
        choices=PRESS_STATUS,
        default='OK'
    )

    class Meta:
        verbose_name_plural = 'presses'

    def __str__(self):
        return str(self.pname)
