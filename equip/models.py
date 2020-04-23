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

    def downtime(self, start_date, end_date):
        dt = 0
        order = self.get_object()
        orders = order.order_set.filter(
            closed=True, date_added__range=(
                start_date, end_date)
        )
        for order in orders:
            dt += order.timerep
        return dt
