from django import forms
from tempus_dominus.widgets import DatePicker


class UploadFileForm(forms.Form):
    file = forms.FileField()


class JobInstForm(forms.Form):
    error_css_class = 'invalid-feedback'
    required_css_class = 'required'
    press = forms.CharField()
    job = forms.CharField()
    comment = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(JobInstForm, self).__init__(*args, **kwargs)
        self.fields['press'].widget.attrs['readonly'] = True
        self.fields['job'].required = False
        self.fields['comment'].required = False

    def clean(self):
        cleaned_data = super().clean()
        cc_job = cleaned_data.get("job")
        try:
            Job.objects.get(name=cc_job)
        except Job.DoesNotExist:
            msg = forms.ValidationError(
                ('Job doesnt exist'),
                code='invalid')
            self.add_error('job', msg)


