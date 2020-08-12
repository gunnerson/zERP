from django.shortcuts import render, redirect
from django.http import Http404
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Record
from staff.models import Employee
from mtn.cm import has_group, is_valid_param


@login_required
def GetID(request):
    if has_group(request.user, 'utility'):
        if request.method != 'POST':
            return render(request, 'pnclk/index.html')
        else:
            employee_id = request.POST.get('employee_id')
            try:
                employee = Employee.objects.get(employee_id=employee_id)
                return redirect('pnclk:rec', pk=employee.id)
            except Employee.DoesNotExist:
                return redirect('pnclk:index')
            except ValueError:
                return redirect('pnclk:index')
    else:
        raise Http404


@login_required
def AddRecord(request, pk):
    if has_group(request.user, 'utility'):
        employee = Employee.objects.get(id=pk)
        try:
            records = Record.objects.filter(employee=employee)
            current_session = records.last()
            if current_session is not None:
                if is_valid_param(current_session.start):
                    session_status = 'punched_in'
                if is_valid_param(current_session.lunchin):
                    session_status = 'lunch_in'
                if is_valid_param(current_session.lunchout):
                    session_status = 'lunch_out'
                if is_valid_param(current_session.end):
                    session_status = 'punched_out'
            else:
                session_status = 'punched_out'
            context['records'] = records
        except Record.DoesNotExist:
            session_status = 'punched_out'
        command = request.GET.get('command')
        if is_valid_param(command):
            if command == 'start':
                Record(
                    employee=employee,
                    start=timezone.now(),
                ).save()
            elif command == 'lunchin':
                current_session.lunchin = timezone.now()
                current_session.save(update_fields=['lunchin'])
            elif command == 'lunchout':
                current_session.lunchout = timezone.now()
                current_session.save(update_fields=['lunchout'])
            elif command == 'end':
                current_session.end = timezone.now()
                current_session.save(update_fields=['end'])
            return redirect('pnclk:index')
        context['session_status'] = session_status
        return render(request, 'pnclk/record.html', context)
    else:
        raise Http404
