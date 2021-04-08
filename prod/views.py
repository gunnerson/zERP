import xlrd
import os
from django.shortcuts import render, redirect
from django.views import View
from datetime import timedelta, datetime, date
from django.utils import timezone
from django.forms import formset_factory
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .models import JobInst
from .forms import UploadFileForm, JobInstForm
from mtn.cm import has_group, is_valid_param, get_url_kwargs, get_shift
from equip.models import Press


@login_required
def upload_sched(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            generate_schedule(request.FILES['file'])
            return redirect('prod:job-list')
    else:
        form = UploadFileForm()
    return render(request, 'prod/sched_upload.html', {'form': form})


@login_required
def auto_upload_sched(request):
    now = timezone.now().date()
    fyear = now.year
    smonth = now.strftime('%b')
    fmonths = (smonth, smonth.upper())
    success = False
    while success == False:
        for fmonth in fmonths:
            fname = '/mnt/rprod/PRODUCTION/Daily Production Report/Daily {0}/{1} Daily {2}.xlsx'.format(
                fyear, fmonth, fyear)
            if os.path.exists(fname):
                f = open(fname, 'rb')
                success = True
                generate_schedule(f)
    return HttpResponse('Operation successful...')


def generate_schedule(f):
    iqs = JobInst.objects.all()
    pqs = Press.objects.all().filter(group='PR').only('pname')
    book = xlrd.open_workbook(file_contents=f.read())
    db_sheet = book.sheet_by_index(5)
    datexl2 = db_sheet.cell(0, 1).value
    xldate2 = xlrd.xldate_as_datetime(datexl2, 0)
    date2 = xldate2.date()
    datexl1 = db_sheet.cell(0, 2).value
    xldate1 = xlrd.xldate_as_datetime(datexl1, 0)
    date1 = xldate1.date()
    press_dict = {}
    for row_idx in range(2, db_sheet.nrows):
        press_id = str(db_sheet.cell(row_idx, 0).value)
        fsj = db_sheet.cell(row_idx, 2).value
        ssj = db_sheet.cell(row_idx, 1).value
        try:
            first_digit = press_id[0]
            if first_digit.isdigit():
                press_name = 'Press ' + f'{int(press_id[:-2]):02}'
            elif first_digit == 'I':
                press_name = 'Inj ' + press_id[3]
            try:
                press = pqs.get(pname=press_name)
                press_dict[press] = {}
                press_dict[press].update({'clocked1': False})
                press_dict[press].update({'clocked2': False})
                if is_valid_param(ssj):
                    try:
                        jobinst = iqs.get(press=press, shift=2, date=date2)
                    except JobInst.DoesNotExist:
                        JobInst(press=press, shift=2, date=date2).save()
                        press_dict[press].update({'clocked2': True})
                if is_valid_param(fsj):
                    try:
                        jobinst = iqs.get(press=press, shift=1, date=date1)
                    except JobInst.DoesNotExist:
                        JobInst(press=press, shift=1, date=date1).save()
                        press_dict[press].update({'clocked1': True})
            except Press.DoesNotExist:
                pass
        except IndexError:
                pass
    for press in press_dict:
        if press_dict[press].get('clocked1'):
            if press.primary:
                procs = press.pmproc_set.all()
                for proc in procs:
                    proc.hours += 8
                    proc.save(update_fields=['hours'])
            else:
                if press_dict[press.press].get('clocked1'):
                    pass
                else:
                    procs = press.press.pmproc_set.all()
                    for proc in procs:
                        proc.hours += 8
                        proc.save(update_fields=['hours'])
        if press_dict[press].get('clocked2'):
            if press.primary:
                procs = press.pmproc_set.all()
                for proc in procs:
                    proc.hours += 8
                    proc.save(update_fields=['hours'])
            else:
                if press_dict[press.press].get('clocked2'):
                    pass
                else:
                    procs = press.press.pmproc_set.all()
                    for proc in procs:
                        proc.hours += 8
                        proc.save(update_fields=['hours'])
        # qs = press.jobinst_set.all().order_by('pk')
        # while qs.count() > 3:
        #     qs[0].delete()


class JobInstListView(LoginRequiredMixin, ListView):
    model = Press
    # paginate_by = 20
    template_name = 'prod/jobinst_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(get_url_kwargs(self.request))
        today = timezone.now().date()
        todayd = today.weekday()
        if todayd == 4:
            tomorrow = today + timedelta(days=3)
        elif todayd == 5:
            tomorrow = today + timedelta(days=2)
        else:
            tomorrow = today + timedelta(days=1)
        context['today'] = today
        context['tomorrow'] = tomorrow
        return context

    def get_queryset(self):
        now = timezone.now().date()
        qs = Press.objects.exclude(jobinst__isnull=True)
        return qs


# class ScheduleView(LoginRequiredMixin, UserPassesTestMixin, CreateView):

#     model = JobInst
#     form_class = JobInstForm
#     template_name = "prod/schedule.html"
#     press_list = Press.objects.filter(group='PR')
#     press_list = press_list.exclude(subgroup='OT')
#     JobInstFormSet = formset_factory(JobInstForm, extra=len(press_list))

#     def get(self, request, *args, **kwargs):
#         formset = self.JobInstFormSet()
#         i = 0
#         for press in self.press_list:
#             formset[i].initial = {'press': press.pname}
#             i += 1
#         context = {
#             'formset': formset,
#         }
#         return render(request, self.template_name, context)

#     def post(self, request, *args, **kwargs):
#         formset = self.JobInstFormSet(self.request.POST)
#         jqs = Job.objects.all()
#         iqs = JobInst.objects.all()
#         if formset.is_valid():
#             date = request.POST.get("dateinput")
#             shift = int(request.POST.get("shiftinput"))
#             try:
#                 dt = datetime.strptime(date, '%m/%d/%Y').date()
#             except ValueError:
#                 dt = None
#             if dt is not None and shift is not None:
#                 for jobinst in formset:
#                     data = jobinst.cleaned_data
#                     press = self.press_list.get(pname=data['press'])
#                     job = jqs.get(name=data['job'])
#                     if is_valid_param(press):
#                         if is_valid_param(data['job']):
#                             jobinst = iqs.filter(
#                                 press=press, job=job).last()
#                             if jobinst is not None:
#                                 if jobinst.shift == shift:
#                                     jobinst.date = dt
#                                     jobinst.save(update_fields=['date'])
#                                 elif jobinst.shift is None:
#                                     jobinst.date = dt
#                                     jobinst.shift = shift
#                                     jobinst.save(update_fields=['date', 'shift'])
#                                 else:
#                                     JobInst(press=press, job=job, shift=shift,
#                                         date=dt).save()
#                             else:
#                                 JobInst(press=press, job=job, shift=shift,
#                                         date=dt).save()
#                         else:
#                             job = press.job(shift=shift)
#                             if job is not None:
#                                 if job.date == dt:
#                                     job.date = None
#                                     job.shift = None
#                                     job.save(update_fields=['date', 'shift'])
#                 return redirect('prod:prod_sched')
#             else:
#                 messages.add_message(
#                     request, messages.INFO, 'Pick date and shift')
#                 return redirect(request.META['HTTP_REFERER'])
#         else:
#             context = {
#                 'formset': formset,
#             }
#             return render(request, self.template_name, context)

#     def test_func(self):
#         return has_group(self.request.user, 'manager')
