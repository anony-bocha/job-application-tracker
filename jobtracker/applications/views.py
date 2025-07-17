from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import logout
from .models import JobApplication
from .forms import JobApplicationForm, InterviewForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def custom_logout(request):
    logout(request)
    return redirect('login')

@login_required
def job_list(request):
    jobs = JobApplication.objects.filter(user=request.user).select_related('company')
    
    filters = {
        'status': request.GET.get('status'),
        'company': request.GET.get('company'),
        'is_remote': request.GET.get('is_remote') == 'on'
    }
    
    if filters['status']:
        jobs = jobs.filter(status=filters['status'])
    if filters['company']:
        jobs = jobs.filter(company__name__icontains=filters['company'])
    if filters['is_remote']:
        jobs = jobs.filter(is_remote=True)

    context = {
        'jobs': jobs.order_by('-applied_date'),
        'status_choices': JobApplication.STATUS_CHOICES,
        'current_filters': filters
    }
    return render(request, 'applications/job_list.html', context)

@login_required
def application_detail(request, pk):
    application = get_object_or_404(
        JobApplication.objects.select_related('company'),
        pk=pk,
        user=request.user
    )
    interviews = application.interview_set.all()
    
    if request.method == 'POST':
        interview_form = InterviewForm(request.POST)
        if interview_form.is_valid():
            interview = interview_form.save(commit=False)
            interview.application = application
            interview.save()
            messages.success(request, 'Interview added!')
            return redirect('application_detail', pk=pk)
    else:
        interview_form = InterviewForm()

    context = {
        'application': application,
        'interviews': interviews,
        'interview_form': interview_form
    }
    return render(request, 'applications/application_detail.html', context)

@login_required
def add_application(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, user=request.user)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            messages.success(request, 'Application added successfully!')
            return redirect('job_list')
    else:
        form = JobApplicationForm(user=request.user)

    return render(request, 'applications/application_form.html', {
        'form': form,
        'title': 'Add New Application'
    })

@login_required
def edit_application(request, pk):
    application = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, instance=application, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application updated!')
            return redirect('application_detail', pk=pk)
    else:
        form = JobApplicationForm(instance=application, user=request.user)

    return render(request, 'applications/application_form.html', {
        'form': form,
        'title': 'Edit Application'
    })

class ApplicationDeleteView(DeleteView):
    model = JobApplication
    success_url = reverse_lazy('job_list')
    template_name = 'applications/confirm_delete.html'
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Application deleted successfully')
        return super().delete(request, *args, **kwargs)
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('job_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})