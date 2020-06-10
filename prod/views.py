import xlrd
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.views.generic.edit import UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from datetime import timedelta

from .models import Job, JobInst
from .forms import UploadFileForm
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
    date = xlrd.xldate_as_datetime(datexl, 0).date()
    for sheet_idx in range(0, 2):
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
                    job = None
                if is_valid_param(press) and is_valid_param(job):
                    if sheet_idx == 1:
                        try:
                            iqs.get(press=press, job=job, shift=sheet_idx,
                                    date=date + timedelta(days=1))
                        except JobInst.DoesNotExist:
                            JobInst.objects.filter(
                                press=press, job=job, shift=sheet_idx).delete()
                            JobInst(press=press, job=job, shift=sheet_idx,
                                    date=date + timedelta(days=1)).save()
                    else:
                        try:
                            iqs.get(press=press, job=job, shift=sheet_idx,
                                    date=date)
                        except JobInst.DoesNotExist:
                            JobInst.objects.filter(
                                press=press, job=job, shift=sheet_idx).delete()
                            JobInst(press=press, job=job, shift=sheet_idx,
                                    date=date).save()
    return redirect('prod:prod_sched')


class JobListView(LoginRequiredMixin, ListView):
    """List of jobs"""
    model = Job
    # paginate_by = 20


class JobCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a job"""
    model = Job

    def test_func(self):
        return has_group(self.request.user, 'maintenance')


class JobUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update job"""
    model = Job

    def test_func(self):
        return has_group(self.request.user, 'maintenance')


class JobInstListView(LoginRequiredMixin, ListView):
    """list scheduled jobs"""
    model = JobInst
    # paginate_by = 20


class JobInstCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Upload a file"""
    model = JobInst

    def test_func(self):
        return has_group(self.request.user, 'manager')


class JobInstUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Add notes"""
    model = JobInst

    def test_func(self):
        return has_group(self.request.user, 'manager')
