import xlrd
from django.shortcuts import render, redirect
from django.views import View
from datetime import timedelta
from django.forms import formset_factory

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
            if is_valid_param(job_name):
                if press_id[0].isdigit():
                    press_name = 'Press ' + f'{int(press_id[:-2]):02}'
                    try:
                        press = pqs.get(pname=press_name)
                    except Press.DoesNotExist:
                        press = None
                if press_id[0] == 'I':
                    try:
                        press = pqs.get(pname=press_id)
                    except Press.DoesNotExist:
                        press = None
                try:
                    job = qs.get(name=job_name)
                except Job.DoesNotExist:
                    job = Job(name=job_name, rate=db_sheet.cell(
                        row_idx, 2).value).save()
                if is_valid_param(press) and is_valid_param(job):
                    try:
                        iqs.get(press=press, job=job, shift=sheet_idx,
                                date=date)
                    except JobInst.DoesNotExist:
                        JobInst.objects.filter(
                            press=press, job=job, shift=sheet_idx).delete()
                        JobInst(press=press, job=job, shift=sheet_idx,
                                date=date).save()
    return redirect('prod:prod_sched')


class ScheduleView(View):
    press_list = Press.objects.filter(group='PR').exclude(subgroup='OT')
    JobInstFormSet = formset_factory(JobInstForm, extra=len(press_list))

    template_name = "prod/schedule.html"

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
        jobinst_formset = self.JobInstFormSet(self.request.POST)
        if jobinst_formset.is_valid():
            for jobinst in jobinst_formset:
                pass
            return redirect('prod:prod_sched')
        else:
            context = {
                'formset': jobinst_formset,
            }
            return render(request, self.template_name, context)

    # def test_func(self):
    #     return has_group(self.request.user, 'manager')
