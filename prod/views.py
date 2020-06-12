import xlrd
from django.shortcuts import render, redirect
from django.views import View
from datetime import timedelta, datetime
from django.forms import formset_factory
from django.views.generic.edit import CreateView
from django.contrib import messages

from .models import Job, JobInst
from .forms import UploadFileForm, JobInstForm
from mtn.cm import has_group, is_valid_param
from equip.models import Press


def upload_sched(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            generate_schedule(request.FILES['file'])
            return redirect('prod:prod_sched')
    else:
        form = UploadFileForm()
    return render(request, 'prod/sched_upload.html', {'form': form})


def generate_schedule(f):
    qs = Job.objects.all().only('name')
    iqs = JobInst.objects.all()
    pqs = Press.objects.all().filter(group='PR').only('pname')
    book = xlrd.open_workbook(file_contents=f.read())
    db_sheet = book.sheet_by_index(4)
    for row_idx in range(0, db_sheet.nrows):
        for col_idx in range(1, 2):
            job = db_sheet.cell(row_idx, 1).value
            rate = db_sheet.cell(row_idx, 2).value
            try:
                qs.get(name=job)
            except Job.DoesNotExist:
                Job(name=job, rate=rate).save()
    firstshift = book.sheet_by_index(0)
    datexl = firstshift.cell(1, 6).value
    date = xlrd.xldate_as_datetime(datexl, 0)
    for sheet_idx in range(0, 3):
        daily_sheet = book.sheet_by_index(sheet_idx)
        for row_idx in range(3, daily_sheet.nrows - 2):
            press_id = str(daily_sheet.cell(row_idx, 0).value)
            job_name = daily_sheet.cell(row_idx, 1).value
            if press_id[0].isdigit():
                press_name = 'Press ' + f'{int(press_id[:-2]):02}'
                try:
                    press = pqs.get(pname=press_name)
                except Press.DoesNotExist:
                    press = None
            elif press_id[0] == 'I':
                try:
                    press = pqs.get(pname=press_id)
                except Press.DoesNotExist:
                    press = None
            if is_valid_param(press):
                if is_valid_param(job_name):
                    try:
                        job = qs.get(name=job_name)
                    except Job.DoesNotExist:
                        job = Job(name=job_name, rate=db_sheet.cell(
                            row_idx, 2).value).save()
                    if is_valid_param(job):
                        jobinst = iqs.filter(
                                press=press, job=job, shift=sheet_idx).last()
                        if jobinst is not None:
                            jobinst.date = date
                            jobinst.save(update_fields=['date'])
                        else:
                            JobInst(press=press, job=job, shift=sheet_idx,
                                    date=date).save()
                else:
                    try:
                        job = press.job()
                        if job.date.date() == date.date() and job.shift == sheet_idx:
                            job.date = None
                            job.shift = None
                            job.save(update_fields=['date', 'shift'])
                            print('>>>>>>>>>>>>>', job.shift)
                    except:
                        pass
    return redirect('prod:prod_sched')


class ScheduleView(CreateView):

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
            job = press.job()
            if job is not None:
                formset[i].initial = {
                    'press': press.pname, 'job': press.job().job.name}
            else:
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
                dt = datetime.strptime(date, '%m/%d/%Y')
            except ValueError:
                try:
                    dt = datetime.strptime(date, '%m/%d/%Y %I:%M %p')
                except ValueError:
                    dt = None
            if dt is not None and shift is not None:
                for jobinst in formset:
                    data = jobinst.cleaned_data
                    press = self.press_list.get(pname=data['press'])
                    job = jqs.get(name=data['job'])
                    if is_valid_param(press) and is_valid_param(data['job']):
                        jobinst = iqs.filter(
                            press=press, job=job, shift=shift).last()
                        if jobinst is not None:
                            jobinst.date = dt
                            jobinst.save(update_fields=['date'])
                        else:
                            JobInst(press=press, job=job, shift=shift,
                                    date=dt).save()
                return redirect('prod:prod_sched')
            else:
                messages.add_message(request, messages.INFO, 'Pick date and shift')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print(formset.errors)
            context = {
                'formset': formset,
            }
            return render(request, self.template_name, context)

    # def test_func(self):
    #     return has_group(self.request.user, 'manager')
