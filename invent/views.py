from django.shortcuts import redirect
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

from .models import Part, UsedPart, Vendor, PartManager, is_valid_param
from .forms import PartCreateForm, VendorCreateForm
from mtn.views import has_group, is_valid_queryparam
from mtn.models import Order


class PartListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    # paginate_by = 20
    count = 0

    def test_func(self):
        return has_group(self.request.user, 'maintenance')

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
        by_vendor = request.GET.get('by_vendor', None)
        if is_valid_param(query) or is_valid_param(by_vendor):
            search_results = Part.objects.search(query, by_vendor)
            qs = sorted(search_results,
                        key=lambda instance: instance.pk,
                        reverse=True)
            self.count = len(qs)
            return qs
        return Part.objects.all()

    def post(self, request, *args, **kwargs):
        order_id = self.kwargs['pk']
        order = Order.objects.get(id=order_id)
        used_part_id = self.request.POST.get('used_part', None)
        used_part = Part.objects.get(id=used_part_id)
        amount = self.request.POST.get('amount', None)
        if int(amount) <= used_part.amount:
            new_used_part = UsedPart(part=used_part, order=order,
                amount_used=amount)
            new_used_part.save()
            used_part.amount -= int(amount)
            used_part.save(update_fields=['amount'])
            return redirect('mtn:order', pk=order_id)
        else:
            messages.add_message(request, messages.INFO, 'Not enough items in stock')
            return redirect(request.META['HTTP_REFERER'])


class PartCreateView(LoginRequiredMixin, CreateView):
    model = Part
    form_class = PartCreateForm

    def test_func(self):
        return has_group(self.request.user, 'maintenance')


class UsedPartListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = UsedPart

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        qs = UsedPart.objects.all().order_by('-order')
        check_marked = self.request.GET.get('check_marked')
        if check_marked:
            qs = qs.filter(marked_to_delete=check_marked)
        return qs

    def post(self, request, *args, **kwargs):
        delete_confirm = self.request.POST.get('delete_confirm')
        if delete_confirm:
            UsedPart.objects.filter(marked_to_delete=True).delete()
            messages.add_message(request, messages.INFO,
                'Marked entries successfully deleted')
        return redirect(request.META['HTTP_REFERER'])


class VendorCreateView(LoginRequiredMixin, CreateView):
    model = Vendor
    form_class = VendorCreateForm

    def test_func(self):
        return has_group(self.request.user, 'maintenance')
