from django.contrib import admin


from equip.models import Press, Upload, Imprint, Job, JobInst

admin.site.register(Press)
admin.site.register(Upload)
admin.site.register(Imprint)
admin.site.register(Job)
admin.site.register(JobInst)
