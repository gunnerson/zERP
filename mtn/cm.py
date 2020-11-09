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
    print('>>>>>>>>>>>shift', shift)
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
