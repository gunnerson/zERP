# Universal methods

from django.contrib.postgres.search import (
    SearchRank,
    SearchVector,
    SearchQuery
)


def dbsearch(queryset, query, config):
    """Search engine"""
    vector = SearchVector('textsearchable_index_col')
    if config == "A":
        query = SearchQuery(query)
        qs = queryset.annotate(rank=SearchRank(vector, query)).filter(
            textsearchable_index_col=query).order_by('-rank')
    if config == "B":
        query_terms = query.split()
        query_terms = ['{0}:*'.format(query_term)
                       for query_term in query_terms]
        tsquery = " & ".join(query_terms)
        qs = queryset.annotate(
            rank=SearchRank(vector, SearchQuery(query))).extra(
            where=["textsearchable_index_col @@ (to_tsquery(%s)) = true"],
            params=[tsquery]).order_by('-rank')
    if config == "C":
        query_terms = query.split()
        tsquery = " & ".join(query_terms)
        tsquery += ":*"
        qs = queryset.annotate(
            rank=SearchRank(vector, SearchQuery(query))).extra(
            where=["textsearchable_index_col @@ (to_tsquery(%s)) = true"],
            params=[tsquery]).order_by('-rank')
    return qs


def is_valid_vendor(param):
    return (param is not None and
            param != 'Choose vendor...' and
            param != 'All vendors'
            )


def is_valid_queryparam(param):
    return param != '' and param is not None


def has_group(user, group_name):
    # Check if the user belongs to a certain group
    return user.groups.filter(name=group_name).exists()
