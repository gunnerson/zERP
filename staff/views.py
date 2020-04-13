from django.shortcuts import render

from .models import Employee


def employees(request):
    """Personnel list."""
    employees = Employee.objects.order_by('first_name')
    context = {'employees': employees}

    return render(request, 'staff/index.html', context)
