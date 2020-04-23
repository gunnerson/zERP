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

    def downtime(self, month, year):
        """Calculate downtime on a monthly basis"""
        dt = 0
        press = self.get_object()
        orders = press.order_set.filter(
            closed=True,
            date_added__year__exact=year,
            date_added__month__exact=month,
        )
        for order in orders:
            dt += order.timerep
        return dt
