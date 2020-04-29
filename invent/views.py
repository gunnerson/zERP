from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

from .models import Part, UsedPart, Vendor, is_valid_param
from .forms import PartCreateForm, VendorCreateForm
from mtn.views import has_group
from mtn.models import Order


class PartListView(LoginRequiredMixin, ListView):
    """List of all parts in the inventory and list of parts to add
    to an existing work order"""
    model = Part
    count = 0
    paginate_by = 20

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # Get order_id for "Back" button in template
        if 'pk' in self.kwargs:
            order_id = self.kwargs['pk']
            context['order_id'] = order_id
        # Keep search fields populated after GET request submitted
        by_vendor = self.request.GET.get('by_vendor', None)
        press_checked = self.request.GET.get('press', None)
        context['count'] = self.count or 0
        context['query'] = self.request.GET.get('query')
        context['by_vendor'] = by_vendor
        context['press_checked'] = press_checked
        context['vendors'] = Vendor.objects.exclude(name__exact=by_vendor)
        return context

    def get_queryset(self):
        # Filter parts by part number, vendor and press
        if 'pk' in self.kwargs:
            order_id = self.kwargs['pk']
            order = Order.objects.get(id=order_id)
            press = order.local
        qs = Part.objects.all().order_by('-pk')
        request = self.request
        query = request.GET.get('query', None)
        by_vendor = request.GET.get('by_vendor', None)
        press_checked = request.GET.get('press', None)
        if is_valid_param(query) or is_valid_param(by_vendor):
            qs = Part.objects.search(query, by_vendor).order_by('-pk')
            self.count = len(qs)
        if press_checked:
            qs = qs.filter(cat=press).order_by('-pk')
        return qs

    def post(self, request, *args, **kwargs):
        # Check if enough in stock, add to work order and subtrack
        # from amount in stock
        order_id = self.kwargs['pk']
        order = Order.objects.get(id=order_id)
        used_part_id = self.request.POST.get('used_part', None)
        used_part = Part.objects.get(id=used_part_id)
        press = order.local
        amount = self.request.POST.get('amount', None)
        if int(amount) <= used_part.amount:
            new_used_part = UsedPart(part=used_part, order=order,
                                     amount_used=amount)
            new_used_part.save()
            used_part.amount -= int(amount)
            used_part.cat.add(press)
            used_part.save(update_fields=['amount'])
            return redirect('mtn:order', pk=order_id)
        else:
            messages.add_message(request, messages.INFO,
                                 'Not enough items in stock')
            return redirect(request.META['HTTP_REFERER'])


class PartCreateView(LoginRequiredMixin, CreateView):
    """Add new part to inventory"""
    model = Part
    form_class = PartCreateForm

    def test_func(self):
        return has_group(self.request.user, 'maintenance')


class PartDetailView(LoginRequiredMixin, DetailView):
    """View part from the inventory"""
    model = Part


class PartUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit part"""
    model = Part
    form_class = PartCreateForm
    template_name = 'invent/part_update_form.html'

    def test_func(self):
        return has_group(self.request.user, 'maintenance')


class UsedPartListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Delete marked parts from work orders"""
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
        used_parts = UsedPart.objects.filter(marked_to_delete=True)
        if delete_confirm:
            # Return deleted to stock
            for upart in used_parts:
                part = upart.part
                part.amount = upart.amount_used + part.amount
                part.save(update_fields=['amount'])
            UsedPart.objects.filter(marked_to_delete=True).delete()
            messages.add_message(request, messages.INFO,
                                 'Marked entries successfully deleted')
        return redirect(request.META['HTTP_REFERER'])


class OrderPartsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Mark used parts in a work order for deletion"""
    model = UsedPart
    template_name = 'invent/delete_part.html'

    def test_func(self):
        return has_group(self.request.user, 'maintenance')

    def get_context_data(self, *args, **kwargs):
        # Get order id for "Back" button in template
        order_id = self.kwargs['pk']
        context = super().get_context_data(*args, **kwargs)
        context['order_id'] = order_id
        return context

    def get_queryset(self):
        # Filter parts associated with requested
        self.order = get_object_or_404(Order, id=self.kwargs['pk'])
        return UsedPart.objects.filter(order=self.order)

    def post(self, request, *args, **kwargs):
        order_id = self.kwargs['pk']
        UsedPart.objects.filter(order_id=order_id).update(
            marked_to_delete=False)
        marked_parts = request.POST.getlist('marked_to_delete')
        for part in marked_parts:
            UsedPart.objects.filter(pk=part).update(marked_to_delete=True)
        return redirect('mtn:order', pk=order_id)


class VendorCreateView(LoginRequiredMixin, CreateView):
    """Add new vendor"""
    model = Vendor
    form_class = VendorCreateForm

    def test_func(self):
        return has_group(self.request.user, 'maintenance')


class VendorDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """View vendor"""
    model = Vendor

    def test_func(self):
        return has_group(self.request.user, 'maintenance')
