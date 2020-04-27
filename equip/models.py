from django.db import models


class Press(models.Model):
    pname = models.CharField(max_length=12)

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
            ordertype='RE',
            date_added__year__exact=year,
            date_added__month__exact=month,
        )
        for order in orders:
            dt += order.timerep.total_seconds() / 3600
        return dt

    def last_pm(self):
        """Last PM date"""
        orders = self.object.order_set.filter(
            closed=True,
            ordertype='PM'
        )
        if orders.exists():
            last_pm_order = orders.last()
            last_pm_date = last_pm_order.repdate
        else:
            last_pm_date = 'Never'
        return last_pm_date
