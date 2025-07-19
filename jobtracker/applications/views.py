from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.http import HttpResponse
import csv
from datetime import timedelta

from .models import JobApplication, Interview, Company, ClientProfile, FreelancerProfile
from .forms import (
    JobFilterForm, UserProfileForm, JobApplicationForm,
    InterviewForm, CustomUserCreationForm
)


# ---------------------------
# Authentication Views
# ---------------------------
def custom_logout(request):
    logout(request)
    return redirect('login')


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')  # Redirect to dashboard instead of job_list for better UX
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


# ---------------------------
# Profile View
# ---------------------------
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


# ---------------------------
# Dashboard View
# ---------------------------
@login_required
def dashboard(request):
    user = request.user

    # Determine role and fetch data accordingly
    if hasattr(user, 'clientprofile'):
        # Client dashboard logic (example: could show projects posted, applications received)
        # Assuming client can view their posted jobs or some stats
        context = {
            'profile': user.clientprofile,
            # Add more client-specific context here
        }
        template = 'applications/client_dashboard.html'

    elif hasattr(user, 'freelancerprofile'):
        # Freelancer dashboard logic (e.g., job applications, interviews)
        user_apps = JobApplication.objects.filter(user=user)
        user_interviews = Interview.objects.filter(application__user=user)

        total_apps = user_apps.count()
        total_interviews = user_interviews.count()
        recent_apps = user_apps.order_by('-applied_date')[:5]
        upcoming_interviews = user_interviews.filter(
            date__gte=timezone.now(),
            date__lte=timezone.now() + timedelta(days=7)
        ).order_by('date')

        context = {
            'total_apps': total_apps,
            'total_interviews': total_interviews,
            'recent_apps': recent_apps,
            'upcoming_interviews': upcoming_interviews,
            'status_counts': user_apps.values('status').annotate(count=Count('status')),
            'source_counts': user_apps.values('source').annotate(count=Count('source')),
            'interview_type_counts': user_interviews.values('interview_type').annotate(count=Count('interview_type')),
            'profile': user.freelancerprofile,
        }
        template = 'applications/freelancer_dashboard.html'

    else:
        # Default fallback if no profile found
        messages.warning(request, "Profile data not found.")
        return redirect('profile')

    return render(request, template, context)


# ---------------------------
# Job Application List View (Freelancer only)
# ---------------------------
@login_required
def job_list(request):
    user = request.user
    # Only freelancers have job applications
    if not hasattr(user, 'freelancerprofile'):
        messages.error(request, "Access denied: This page is for freelancers only.")
        return redirect('dashboard')

    applications = JobApplication.objects.filter(user=user).order_by('-applied_date')

    form = JobFilterForm(request.GET or None, user=user)
    if form.is_valid():
        status = form.cleaned_data.get('status')
        source = form.cleaned_data.get('source')
        search = form.cleaned_data.get('search')
        tags = form.cleaned_data.get('tags')

        if status:
            applications = applications.filter(status=status)
        if source:
            applications = applications.filter(source=source)
        if search:
            applications = applications.filter(
                Q(company__name__icontains=search) |
                Q(position__icontains=search) |
                Q(notes__icontains=search)
            )
        if tags:
            applications = applications.filter(tags__in=tags).distinct()

    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'applications': page_obj,
        'form': form,
        'total_applications': applications.count(),
        'total_offers': applications.filter(status='OF').count(),
        'total_rejected': applications.filter(status='RJ').count(),
        'total_accepted': applications.filter(status='AC').count(),
    }
    return render(request, 'applications/job_list.html', context)


# ---------------------------
# Job Application Detail View (Freelancer only)
# ---------------------------
@login_required
def application_detail(request, pk):
    user = request.user
    if not hasattr(user, 'freelancerprofile'):
        messages.error(request, "Access denied: This page is for freelancers only.")
        return redirect('dashboard')

    application = get_object_or_404(JobApplication.objects.select_related('company'), pk=pk, user=user)
    interviews = application.interviews.all()

    if request.method == 'POST':
        interview_form = InterviewForm(request.POST)
        if interview_form.is_valid():
            interview = interview_form.save(commit=False)
            interview.application = application
            interview.save()
            messages.success(request, 'Interview added successfully.')
            return redirect('application_detail', pk=pk)
    else:
        interview_form = InterviewForm()

    context = {
        'application': application,
        'interviews': interviews,
        'interview_form': interview_form,
    }
    return render(request, 'applications/application_detail.html', context)


# ---------------------------
# Add Job Application (Freelancer only)
# ---------------------------
@login_required
def add_application(request):
    user = request.user
    if not hasattr(user, 'freelancerprofile'):
        messages.error(request, "Access denied: This page is for freelancers only.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, user=user)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = user
            application.save()
            form.save_m2m()
            messages.success(request, 'Application added successfully!')
            return redirect('job_list')
    else:
        form = JobApplicationForm(user=user)

    return render(request, 'applications/application_form.html', {
        'form': form,
        'title': 'Add New Application'
    })


# ---------------------------
# Edit Job Application (Freelancer only)
# ---------------------------
@login_required
def edit_application(request, pk):
    user = request.user
    if not hasattr(user, 'freelancerprofile'):
        messages.error(request, "Access denied: This page is for freelancers only.")
        return redirect('dashboard')

    application = get_object_or_404(JobApplication, pk=pk, user=user)
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, instance=application, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application updated successfully!')
            return redirect('application_detail', pk=pk)
    else:
        form = JobApplicationForm(instance=application, user=user)

    return render(request, 'applications/application_form.html', {
        'form': form,
        'title': 'Edit Application'
    })


# ---------------------------
# Delete Job Application (Freelancer only)
# ---------------------------
class ApplicationDeleteView(DeleteView):
    model = JobApplication
    success_url = reverse_lazy('job_list')
    template_name = 'applications/confirm_delete.html'

    def get_queryset(self):
        # Ensure only freelancer's own applications are deletable
        user = self.request.user
        if not hasattr(user, 'freelancerprofile'):
            return JobApplication.objects.none()
        return super().get_queryset().filter(user=user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Application deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ---------------------------
# Export Applications CSV (Freelancer only)
# ---------------------------
@login_required
def export_applications_csv(request):
    user = request.user
    if not hasattr(user, 'freelancerprofile'):
        messages.error(request, "Access denied: This action is for freelancers only.")
        return redirect('dashboard')

    applications = JobApplication.objects.filter(user=user).order_by('-applied_date')

    # Apply filters
    status = request.GET.get('status')
    source = request.GET.get('source')
    search = request.GET.get('search')

    if status:
        applications = applications.filter(status=status)
    if source:
        applications = applications.filter(source=source)
    if search:
        applications = applications.filter(
            Q(company__name__icontains=search) |
            Q(position__icontains=search) |
            Q(notes__icontains=search)
        )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="job_applications.csv"'

    writer = csv.writer(response)
    writer.writerow(['Company', 'Position', 'Status', 'Source', 'Applied Date', 'Salary Min', 'Salary Max', 'Is Remote'])

    for app in applications:
        writer.writerow([
            app.company.name,
            app.position,
            app.get_status_display(),
            app.get_source_display(),
            app.applied_date,
            app.salary_min,
            app.salary_max,
            "Yes" if app.is_remote else "No"
        ])

    return response
