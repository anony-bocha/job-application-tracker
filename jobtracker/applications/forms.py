from django import forms
from .models import JobApplication, Company, Interview

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = [
            'company', 'position', 'status', 'source',
            'applied_date', 'notes', 'salary_min',
            'salary_max', 'is_remote', 'referral_contact'
        ]
        widgets = {
            'applied_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['company'].queryset = Company.objects.filter(
                jobapplication__user=user
            ).distinct()
        else:
            self.fields['company'].queryset = Company.objects.all()

class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['interview_type', 'interviewer', 'date', 'notes', 'follow_up']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
