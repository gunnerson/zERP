from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Part, UsedPart, Vendor
from .forms import PartCreateForm, VendorCreateForm
from mtn.cm import has_group, is_valid_vendor, is_valid_param, \
    get_url_kwargs, is_empty_param
from mtn.models import Order
from equip.models import Press


class PartListView(LoginRequiredMixin, ListView):
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
        order_id = self.kwargs['pk']
        order = Order.objects.get(id=order_id)
        added_parts = order.parts.all()
        used_part_id = self.request.POST.get('used_part', None)
        used_part = Part.objects.get(id=used_part_id)
        if used_part in added_parts:
            messages.add_message(request, messages.INFO,
                                 'Part has already been added')
            return redirect(request.META['HTTP_REFERER'])
        else:
            press = order.local
            amount = self.request.POST.get('amount', None)
            if int(amount) <= used_part.amount:
                new_used_part = UsedPart(part=used_part, amount_used=amount)
                new_used_part.order = order
                new_used_part.save()
                used_part.amount -= int(amount)
                used_part.cat.add(press)
                used_part.save(update_fields=['amount'])
                return redirect('mtn:edit_order', pk=order_id)
            else:
                messages.add_message(request, messages.INFO,
                                     'Not enough items in stock')
                return redirect(request.META['HTTP_REFERER'])


# @login_required
# def import_parts(request, pk):
#     press = Press.objects.get(id=pk)
#     last_pm = press.last_pm()
#     cur_pm = press.pm_set.get(closed=False)
#     cur_used_parts = cur_pm.usedpart_set.all()
#     partlist = cur_used_parts.values_list('part_id', flat=True)
#     if last_pm is not None:
#         last_used_parts = last_pm.usedpart_set.all()
#         for used_part in last_used_parts:
#             if used_part.part.id not in partlist:
#                 amount = used_part.amount_used
#                 if amount <= used_part.part.amount:
#                     new_part = used_part
#                     new_part.pk = None
#                     new_part.pm = cur_pm
#                     used_part.part.amount -= amount
#                     new_part.save()
#                     used_part.part.save(update_fields=['amount'])
#                 else:
#                     messages.add_message(request, messages.INFO,
#                                          'Not enough items in stock for part: \
#                                     {0}'.format(used_part.part))
#     return redirect(request.META['HTTP_REFERER'])


class PartCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Part
    form_class = PartCreateForm

    def test_func(self):
        if (has_group(self.request.user, 'maintenance') or
                has_group(self.request.user, 'supervisor')):
            test_func = True
        else:
            test_func = False
        return test_func

    def form_valid(self, form):
        self.object = form.save()
        if is_empty_param(self.object.partnum):
            self.object.partnum = str(f'{self.object.id:06}')
            self.object.save(update_fields=['partnum'])
        return redirect('invent:partlist')


class PartDetailView(LoginRequiredMixin, DetailView):
    model = Part

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['uploads'] = self.object.upload_set.all()
        return context


class PartUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
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


class OrderPartsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = UsedPart
    template_name = 'invent/update_parts.html'

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
        return self.order.usedpart_set.all()


    def post(self, request, *args, **kwargs):
        order_id = self.kwargs['pk']
        for key, value in request.POST.items():
            try:
                value = int(value)
                usedpart = UsedPart.objects.get(id=key)
                amount_before = usedpart.amount_used
                if value == 0:
                    usedpart.part.amount += amount_before
                    usedpart.part.save(update_fields=['amount'])
                    usedpart.delete()
                elif amount_before != value:
                    if usedpart.part.amount >= value - amount_before:
                        usedpart.part.amount += amount_before - value
                        usedpart.amount_used = value
                        usedpart.save(update_fields=['amount_used'])
                        usedpart.part.save(update_fields=['amount'])
                    else:
                        messages.add_message(request, messages.INFO,
                                             'Not enough items in stock for part: \
                                {0}'.format(usedpart.part.partnum))
                        return redirect(request.META['HTTP_REFERER'])
            except UsedPart.DoesNotExist:
                pass
            except ValueError:
                pass
        return redirect('mtn:order', pk=order_id)


class VendorListView(LoginRequiredMixin, ListView):
    model = Vendor
    paginate_by = 50


class VendorCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
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
    model = Vendor


class VendorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
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
