from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Part, Vendor, PartManager, is_valid_param
from .forms import PartForm, VendorForm
from mtn.views import has_group


class PartListView(LoginRequiredMixin, ListView):
    template_name = 'invent/part_list.html'
    paginate_by = 20
    count = 0

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        by_vendor = self.request.GET.get('by_vendor', None)
        context['count'] = self.count or 0
        context['query'] = self.request.GET.get('query')
        context['by_vendor'] = by_vendor
        context['vendors'] = Vendor.objects.exclude(name__exact=by_vendor)
        return context

    def get_queryset(self):
        request = self.request
        query = request.GET.get('query', None)
        by_vendor = request.GET.get('by_vendor')

        if is_valid_param(query) or is_valid_param(by_vendor):
            search_results = Part.objects.search(query, by_vendor)
            qs = sorted(search_results,
                        key=lambda instance: instance.pk,
                        reverse=True)
            self.count = len(qs)
            return qs
        return Part.objects.all()


@login_required
def new_part(request):
    """Add new part"""
    if has_group(request.user, 'maintenance'):

        if request.method != 'POST':
            # No data submitted; create a blank form.
            form = PartForm()

        else:
        # POST data submitted; process data.
            form = PartForm(data=request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('invent:partlist'))

    else:
        raise Http404

    context = {'form': form}
    return render(request, 'invent/new_part.html', context)


@login_required
def new_vendor(request):
    """Add new part"""
    if has_group(request.user, 'maintenance'):

        if request.method != 'POST':
            # No data submitted; create a blank form.
            form = VendorForm()

        else:
        # POST data submitted; process data.
            form = VendorForm(data=request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('invent:partlist'))

    else:
        raise Http404

    context = {'form': form}
    return render(request, 'invent/new_vendor.html', context)
