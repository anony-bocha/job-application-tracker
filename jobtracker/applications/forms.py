from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column
from crispy_forms.bootstrap import PrependedText

from .models import JobApplication, Company, Interview, Tag

# --------------------------
# Job Filter Form
# --------------------------
class JobFilterForm(forms.Form):
    """
    Allows filtering the job list by status, source, search, and tags.
    """
    STATUS_CHOICES = [('', 'All')] + list(JobApplication.STATUS_CHOICES)
    SOURCE_CHOICES = [('', 'All')] + list(JobApplication.SOURCE_CHOICES)

    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label='Status')
    source = forms.ChoiceField(choices=SOURCE_CHOICES, required=False, label='Source')
    search = forms.CharField(max_length=100, required=False, label='Search')
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Tags'
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            # Future: Filter tags to user-specific tags if implemented
            self.fields['tags'].queryset = Tag.objects.all()

# --------------------------
# User Profile Form
# --------------------------
class UserProfileForm(forms.ModelForm):
    """
    Allows users to edit their profile details.
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

# --------------------------
# Custom User Creation Form
# --------------------------
class CustomUserCreationForm(UserCreationForm):
    """
    Custom sign-up form using crispy forms for clean layout.
    """
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column(PrependedText('username', '<i class="bi bi-person-fill"></i>'), css_class='col-md-6'),
                Column(PrependedText('email', '<i class="bi bi-envelope-fill"></i>'), css_class='col-md-6'),
            ),
            Row(
                Column(PrependedText('first_name', '<i class="bi bi-person-badge-fill"></i>'), css_class='col-md-6'),
                Column(PrependedText('last_name', '<i class="bi bi-person-badge-fill"></i>'), css_class='col-md-6'),
            ),
            Row(
                Column(PrependedText('password1', '<i class="bi bi-lock-fill"></i>'), css_class='col-md-6'),
                Column(PrependedText('password2', '<i class="bi bi-lock-fill"></i>'), css_class='col-md-6'),
            ),
            Submit('submit', 'Sign Up', css_class='btn btn-primary btn-block mt-3')
        )

# --------------------------
# Job Application Form
# --------------------------
class JobApplicationForm(forms.ModelForm):
    """
    Form to create or update a job application.
    """
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Tags'
    )

    class Meta:
        model = JobApplication
        fields = [
            'company', 'position', 'status', 'source',
            'applied_date', 'notes', 'salary_min',
            'salary_max', 'is_remote', 'referral_contact', 'tags'
        ]
        widgets = {
            'applied_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['company'].queryset = Company.objects.filter(applications__user=user).distinct()
            self.fields['tags'].queryset = Tag.objects.filter(applications__user=user).distinct()
        else:
            self.fields['company'].queryset = Company.objects.all()
            self.fields['tags'].queryset = Tag.objects.all()

# --------------------------
# Interview Form
# --------------------------
class InterviewForm(forms.ModelForm):
    """
    Form to add or edit an interview linked to a job application.
    """
    class Meta:
        model = Interview
        fields = ['interview_type', 'interviewer', 'date', 'notes', 'follow_up']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
