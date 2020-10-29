import xlrd
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
    for row_idx in range(2, db_sheet.nrows):
        press_id = str(db_sheet.cell(row_idx, 0).value)
        fsj = db_sheet.cell(row_idx, 2).value
        ssj = db_sheet.cell(row_idx, 1).value
        if press_id[0].isdigit():
            press_name = 'Press ' + f'{int(press_id[:-2]):02}'
            try:
                press = pqs.get(pname=press_name)
            except Press.DoesNotExist:
                press = None
        elif press_id[0] == 'I':
            press_name = 'Inj ' + press_id[3]
            try:
                press = pqs.get(pname=press_name)
            except Press.DoesNotExist:
                press = None
        if is_valid_param(press):
            if is_valid_param(fsj):
                try:
                    jobinst = iqs.get(press=press, shift=1, date=date1)
                except JobInst.DoesNotExist:
                    JobInst(press=press, shift=1, date=date1).save()
                    procs = press.pmproc_set.all()
                    for proc in procs:
                        proc.hours += 8
                        proc.save(update_fields=['hours'])
            if is_valid_param(ssj):
                try:
                    jobinst = iqs.get(press=press, shift=2, date=date2)
                except JobInst.DoesNotExist:
                    JobInst(press=press, shift=2, date=date2).save()
                    procs = press.pmproc_set.all()
                    for proc in procs:
                        proc.hours += 8
                        proc.save(update_fields=['hours'])


# def generate_schedule(f):
#     qs = Job.objects.all().only('name')
#     iqs = JobInst.objects.all()
#     pqs = Press.objects.all().filter(group='PR').only('pname')
#     book = xlrd.open_workbook(file_contents=f.read())
#     db_sheet = book.sheet_by_index(4)
#     for row_idx in range(0, db_sheet.nrows):
#         for col_idx in range(1, 2):
#             job = db_sheet.cell(row_idx, 1).value
#             rate = db_sheet.cell(row_idx, 2).value
#             try:
#                 qs.get(name=job)
#             except Job.DoesNotExist:
#                 Job(name=job, rate=rate).save()
#     for sheet_idx in range(0, 3):
#         daily_sheet = book.sheet_by_index(sheet_idx)
#         datexl = daily_sheet.cell(1, 6).value
#         xldate = xlrd.xldate_as_datetime(datexl, 0)
#         date = xldate.date()
#         for row_idx in range(3, daily_sheet.nrows - 2):
#             press_id = str(daily_sheet.cell(row_idx, 0).value)
#             job_name = daily_sheet.cell(row_idx, 1).value
#             if press_id[0].isdigit():
#                 press_name = 'Press ' + f'{int(press_id[:-2]):02}'
#                 try:
#                     press = pqs.get(pname=press_name)
#                 except Press.DoesNotExist:
#                     press = None
#             elif press_id[0] == 'I':
#                 try:
#                     press = pqs.get(pname=press_id)
#                 except Press.DoesNotExist:
#                     press = None
#             if is_valid_param(press):
#                 if is_valid_param(job_name):
#                     try:
#                         job = qs.get(name=job_name)
#                     except Job.DoesNotExist:
#                         job = Job(name=job_name, rate=db_sheet.cell(
#                             row_idx, 2).value).save()
#                     if is_valid_param(job):
#                         jobinst = iqs.filter(
#                             press=press, job=job, shift=sheet_idx).last()
#                         if jobinst is not None:
#                             jobinst.date = date
#                             jobinst.save(update_fields=['date'])
#                         else:
#                             JobInst(press=press, job=job, shift=sheet_idx,
#                                     date=date).save()
#                 else:
#                     try:
#                         job = press.job(shift=sheet_idx)
#                         if job.date == date:
#                             job.date = None
#                             job.shift = None
#                             job.save(update_fields=['date', 'shift'])
#                     except JobInst.DoesNotExist:
#                         pass
#                     except AttributeError:
#                         pass


class ScheduleView(LoginRequiredMixin, UserPassesTestMixin, CreateView):

    model = JobInst
    form_class = JobInstForm
    template_name = "prod/schedule.html"
    press_list = Press.objects.filter(group='PR')
    press_list = press_list.exclude(subgroup='OT')
    JobInstFormSet = formset_factory(JobInstForm, extra=len(press_list))

    def get(self, request, *args, **kwargs):
        formset = self.JobInstFormSet()
        i = 0
        for press in self.press_list:
            formset[i].initial = {'press': press.pname}
            i += 1
        context = {
            'formset': formset,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        formset = self.JobInstFormSet(self.request.POST)
        jqs = Job.objects.all()
        iqs = JobInst.objects.all()
        if formset.is_valid():
            date = request.POST.get("dateinput")
            shift = int(request.POST.get("shiftinput"))
            try:
                dt = datetime.strptime(date, '%m/%d/%Y').date()
            except ValueError:
                dt = None
            if dt is not None and shift is not None:
                for jobinst in formset:
                    data = jobinst.cleaned_data
                    press = self.press_list.get(pname=data['press'])
                    job = jqs.get(name=data['job'])
                    if is_valid_param(press):
                        if is_valid_param(data['job']):
                            jobinst = iqs.filter(
                                press=press, job=job).last()
                            if jobinst is not None:
                                if jobinst.shift == shift:
                                    jobinst.date = dt
                                    jobinst.save(update_fields=['date'])
                                elif jobinst.shift is None:
                                    jobinst.date = dt
                                    jobinst.shift = shift
                                    jobinst.save(update_fields=['date', 'shift'])
                                else:
                                    JobInst(press=press, job=job, shift=shift,
                                        date=dt).save()
                            else:
                                JobInst(press=press, job=job, shift=shift,
                                        date=dt).save()
                        else:
                            job = press.job(shift=shift)
                            if job is not None:
                                if job.date == dt:
                                    job.date = None
                                    job.shift = None
                                    job.save(update_fields=['date', 'shift'])
                return redirect('prod:prod_sched')
            else:
                messages.add_message(
                    request, messages.INFO, 'Pick date and shift')
                return redirect(request.META['HTTP_REFERER'])
        else:
            context = {
                'formset': formset,
            }
            return render(request, self.template_name, context)

    def test_func(self):
        return has_group(self.request.user, 'manager')


class JobInstListView(LoginRequiredMixin, ListView):
    """List of scheduled jobs"""
    model = JobInst
    # count = 0
    # paginate_by = 20

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(get_url_kwargs(self.request))
        dateinput = self.request.GET.get('dateinput', date.today())
        # try:
        #     del context['dateinput']
        # except KeyError:
        #     pass
        context['dateinput'] = dateinput
        context['shift'] = get_shift()
        return context

    def get_queryset(self):
        qs = JobInst.objects.all().order_by('press')
        dateinput = self.request.GET.get('dateinput', None)
        shiftinput = self.request.GET.get('shiftinput', get_shift())
        if is_valid_param(dateinput):
            dt = datetime.strptime(dateinput, '%m/%d/%Y')
        else:
            dt = timezone.localtime(timezone.now()).date()
        qs = qs.filter(date=dt, shift=shiftinput)
        return qs
