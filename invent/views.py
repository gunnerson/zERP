from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

from .models import Part, UsedPart, Vendor
from .forms import PartCreateForm, VendorCreateForm
from mtn.cm import has_group, is_valid_vendor, is_valid_param, get_url_kwargs
from mtn.models import Order


class PartListView(LoginRequiredMixin, ListView):
    """List of all parts in the inventory and list of parts to add
    to an existing work order"""
    model = Part
    paginate_by = 50
    count = 0

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(get_url_kwargs(self.request))
        vendor = context.get('vendor', None)
        context['count'] = self.count or 0
        context['vendors'] = Vendor.objects.exclude(name__exact=vendor)
        return context

    def get_queryset(self):
        # Filter parts by part number, vendor and press
        if 'pk' in self.kwargs:
            order = Order.objects.get(id=self.kwargs['pk'])
        qs = Part.objects.all()
        request = self.request
        query = request.GET.get('query', None)
        vendor = request.GET.get('vendor', None)
        press = request.GET.get('press', None)
        if is_valid_param(query) or is_valid_vendor(vendor):
            qs = Part.objects.search(query, vendor)
            self.count = len(qs)
        if press:
            qs = qs.filter(cat=order.local)
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


class PartCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Add new part to inventory"""
    model = Part
    form_class = PartCreateForm

    def test_func(self):
        if (has_group(self.request.user, 'maintenance') or
                has_group(self.request.user, 'supervisor')):
            test_func = True
        else:
            test_func = False
        return test_func


class PartDetailView(LoginRequiredMixin, DetailView):
    """View part from the inventory"""
    model = Part


class PartUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit part"""
    model = Part
    form_class = PartCreateForm
    template_name = 'invent/part_update_form.html'

    def test_func(self):
        if (has_group(self.request.user, 'maintenance') or
                has_group(self.request.user, 'supervisor')):
            test_func = True
        else:
            test_func = False
        return test_func


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


class VendorListView(LoginRequiredMixin, ListView):
    """List Vendors"""
    model = Vendor
    paginate_by = 50


class VendorCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Add new vendor"""
    model = Vendor
    form_class = VendorCreateForm

    def test_func(self):
        if (has_group(self.request.user, 'maintenance') or
                has_group(self.request.user, 'supervisor')):
            test_func = True
        else:
            test_func = False
        return test_func


class VendorDetailView(LoginRequiredMixin, DetailView):
    """View vendor"""
    model = Vendor


class VendorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Add new vendor"""
    model = Vendor
    form_class = VendorCreateForm
    template_name = 'invent/vendor_update_form.html'

    def test_func(self):
        if (has_group(self.request.user, 'maintenance') or
                has_group(self.request.user, 'supervisor')):
            test_func = True
        else:
            test_func = False
        return test_func
