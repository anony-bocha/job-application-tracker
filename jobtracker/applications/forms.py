from django import forms
from .models import JobApplication

STATUS_CHOICES = [
    ('Applied', 'Applied'),
    ('Interview', 'Interview'),
    ('Offer', 'Offer'),
    ('Rejected', 'Rejected'),
]

class JobApplicationForm(forms.ModelForm):
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), required=False)

    class Meta:
        model = JobApplication
        fields = ['company', 'position', 'status', 'notes']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
        }