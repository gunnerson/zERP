# Universal methods

from django.contrib.postgres.search import (
    SearchRank,
    SearchVector,
    SearchQuery,
)


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
                p_name += "{0}={1}&".format(key,value)
        context['page_kwargs'] = p_name
        return context
