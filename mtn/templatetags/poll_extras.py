from django import template

from equip.models import Press

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter
def press_status(press_id):
    """Get press status"""
    press = Press.objects.get(id=press_id)
    last_order = press.order_set.filter(closed=False).last()
    if last_order is not None:
        press_status = last_order.ordertype
    else:
        press_status = 'OK'
    return press_status


# @register.filter()
# def smooth_timedelta(timedeltaobj):
#     """Convert a datetime.timedelta object into Hours, Minutes, Seconds."""
#     secs = timedeltaobj.total_seconds()
#     timetot = ""
#     if secs > 86400: # 60sec * 60min * 24hrs
#         days = secs // 86400
#         timetot += "{} days".format(int(days))
#         secs = secs - days*86400

#     if secs > 3600:
#         hrs = secs // 3600
#         timetot += " {} hours".format(int(hrs))
#         secs = secs - hrs*3600

#     if secs > 60:
#         mins = secs // 60
#         timetot += " {} minutes".format(int(mins))
#         secs = secs - mins*60

#     if secs > 0:
#         timetot += " {} seconds".format(int(secs))
#     return timetot
