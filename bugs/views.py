from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Bug
from .forms import BugCreateForm


class BugCreateView(LoginRequiredMixin, CreateView):
    """Report a bug"""
    model = Bug
    form_class = BugCreateForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        previous_page = self.request.POST.get('previous_page', None)
        self.object.metadata = previous_page
        self.object.save()
        return redirect(previous_page)
