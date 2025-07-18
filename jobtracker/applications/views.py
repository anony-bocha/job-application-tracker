from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import (
    JobFilterForm, UserProfileForm, JobApplicationForm,
    InterviewForm, CustomUserCreationForm
)
from .models import JobApplication

def custom_logout(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'registration/profile.html', {'form': form})

@login_required
def job_list(request):
    applications = JobApplication.objects.filter(user=request.user).order_by('-applied_date')
    form = JobFilterForm(request.GET or None)

    if form.is_valid():
        status = form.cleaned_data.get('status')
        source = form.cleaned_data.get('source')
        search = form.cleaned_data.get('search')

        if status:
            applications = applications.filter(status=status)
        if source:
            applications = applications.filter(source=source)
        if search:
            applications = applications.filter(
                models.Q(company__name__icontains=search) |
                models.Q(position__icontains=search)
            )

    # Pagination
    paginator = Paginator(applications, 10)  # Show 10 applications per page
    page_number = request.GET.get('page')
    try:
        applications_page = paginator.page(page_number)
    except PageNotAnInteger:
        applications_page = paginator.page(1)
    except EmptyPage:
        applications_page = paginator.page(paginator.num_pages)

    # Dashboard summary
    total_applications = applications.count()
    total_offers = applications.filter(status='OF').count()
    total_rejected = applications.filter(status='RJ').count()
    total_accepted = applications.filter(status='AC').count()

    context = {
        'applications': applications_page,
        'form': form,
        'total_applications': total_applications,
        'total_offers': total_offers,
        'total_rejected': total_rejected,
        'total_accepted': total_accepted,
    }
    return render(request, 'applications/job_list.html', context)


@login_required
def dashboard(request):
    user_apps = JobApplication.objects.filter(user=request.user)

    total_apps = user_apps.count()
    status_counts = user_apps.values('status').annotate(count=Count('status'))
    source_counts = user_apps.values('source').annotate(count=Count('source'))

    recent_apps = user_apps.order_by('-applied_date')[:5]

    return render(request, 'applications/dashboard.html', {
        'total_apps': total_apps,
        'status_counts': status_counts,
        'source_counts': source_counts,
        'recent_apps': recent_apps,
    })

@login_required
def application_detail(request, pk):
    application = get_object_or_404(
        JobApplication.objects.select_related('company'),
        pk=pk,
        user=request.user
    )
    interviews = application.interviews.all()

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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('job_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
