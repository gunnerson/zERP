# Universal methods

from django.contrib.postgres.search import (
    SearchRank,
    SearchVector,
    SearchQuery,
)
from django.utils import timezone


def dbsearch(queryset, query, config, *args):
    """Search engine"""
    vector = SearchVector(*args, config='english')

    if config == "A":
        query = SearchQuery(query, search_type="raw")
        qs = queryset.annotate(
            search=vector,
            rank=SearchRank(vector, query)).filter(
            search=query).order_by('-rank')

    if config == "B":
        query_terms = query.split()
        query_terms = ['{0}:*'.format(query_term)
                       for query_term in query_terms]
        tsquery = " & ".join(query_terms)
        query = SearchQuery(tsquery, search_type="raw")
        qs = queryset.annotate(
            search=vector,
            rank=SearchRank(vector, query)).filter(
            search=query).order_by('-rank')

    if config == "C":
        query_terms = query.split()
        tsquery = " & ".join(query_terms)
        tsquery += ":*"
        query = SearchQuery(tsquery, search_type="raw")
        qs = queryset.annotate(
            search=vector,
            rank=SearchRank(vector, query)).filter(
            search=query).order_by('-rank')

    return qs


def is_valid_vendor(param):
    return (param is not None and
            param != 'Choose vendor...' and
            param != 'All vendors'
            )


def is_valid_param(param):
    return param != '' and param is not None


def is_empty_param(param):
    return param == '' or param is None


def has_group(user, group_name):
    # Check if the user belongs to a certain group
    return user.groups.filter(name=group_name).exists()


def get_url_kwargs(request):
    rkwargs = list(request.GET.items())
    context = {}
    p_name = ""
    if rkwargs is not None:
        for key, value in rkwargs:
            if is_valid_param(value) and key != 'page':
                context[key] = value
                p_name += "{0}={1}&".format(key, value)
        context['page_kwargs'] = p_name
        return context


def get_shift():
    now = timezone.localtime(timezone.now())
    nowh = now.hour
    nowm = now.minute
    if nowh in range(7, 15):
        shift = 1
    elif nowh in range(16, 23):
        shift = 2
    elif nowh == 15:
        if nowm < 30:
            shift = 1
        else:
            shift = 2
    else:
        shift = None
    return shift

    # if(!!window.performance && window.performance.navigation.type == 2)
    # {
    #     window.location.reload();
    # }

    # var btns = document.querySelectorAll(".repairToggle");
    # for (i = 0; i < btns.length; i++) {
    #   btns[i].addEventListener("click", manageOrderStatus);
    # }
    # function manageOrderStatus() {
    #   var order_id = this.getAttribute("order_id");
    #   var func = this.getAttribute("func");
    #   var btn = this;
    #   var endpoint = "{% url 'mtn:ajax_repair_toggle' %}";
    #   $.ajax({
    #     url: endpoint,
    #     type: "GET",
    #     data: {
    #       'order_id': order_id,
    #       'func': func,
    #     },
    #     success: function (data) {
    #       $(btn).html(data);
    #       if(func == 'start'){
    #         btn.setAttribute("func", "stop");
    #       } else {
    #         btn.setAttribute("func", "start");
    #       }
    #     },
    #     error: function (error_data) {
    #       console.log(error_data)
    #     }
    #   });
    # }


def time_delay(request):
    from math import sqrt
    from django.shortcuts import render

    # Time Alignment Delay Calculator

    # Constants
    TP = 2.750
    YM = 0.125
    YT = 0.022
    XB = 0.370
    XT = 0.052
    sound_speed = 343.2

    MP = round(sqrt(pow(YM, 2) + pow(YT + TP, 2)), 3)
    BP = round(sqrt(pow(XB, 2) + pow(XT + TP, 2)), 3)
    mid_path = round((MP - TP), 3)
    low_path = round((BP - MP), 3)
    print('Extra MID path = ', int(mid_path * 1000), ' mm')
    print('Extra LF path = ', int(low_path * 1000), ' mm')
    tweeter_delay = round((mid_path / sound_speed), 6)
    mid_delay = round((low_path / sound_speed), 6)
    print('Tweeter delay = ', int(tweeter_delay * 1000000), ' usec')
    print('Mid delay = ', int(mid_delay * 1000000), ' usec')

    # Filter resistors calculator

    e24_multipliers = (1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7,
                       3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5,
                       8.2, 9.1)
    resistors = []
    itera = len(e24_multipliers)
    for i in range(0, (itera - 1), 1):
        resistors.append(int(round((e24_multipliers[i] * 100), 0)))
    # for i in range(0, (itera - 1), 1):
    #     resistors.append(int(round((e24_multipliers[i] * 1000), 0)))
    # for i in range(0, (itera - 1), 1):
    #     resistors.append(int(round((e24_multipliers[i] * 10000), 0)))

    required_value = 97.7
    x = 0.01
    best_result = 1000

    for i in range(len(resistors) - 1):
        r1 = resistors[i]
        for i2 in range(len(resistors) - 1):
            r2 = resistors[i2]
            impedance = r1 * r2 / (r1 + r2)
            error = abs((impedance - required_value) / required_value)
            # standart_deviation = sqrt((pow(r1 * x, 2) + pow(r2 * x, 2) / 2))
            deviation = r1 * x / (1 + r1 / r2) + r2 * x / (1 + r2 / r1)
            if error < best_result:
                best_result = error

                print('R1 = ', r1, ' Ohm, R2 = ', r2,
                      ' Ohm, Impedance = ', impedance, ' Ohm, Error = ', round(error * 100, 2), '%, Deviation = ', round(deviation, 4), '%')
    return render(request, 'mtn/index.html')
