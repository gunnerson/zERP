from django.contrib import admin

from prod.models import Job, JobInst

admin.site.register(Job)
admin.site.register(JobInst)
