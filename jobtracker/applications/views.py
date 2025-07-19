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

from .models import (
    JobPosting, JobApplication, Interview,
    Company, ClientProfile, FreelancerProfile
)
from .forms import (
    JobFilterForm, UserProfileForm, JobApplicationForm,
    InterviewForm, CustomUserCreationForm, JobPostingForm
)
from applications.utils import send_application_notification


@login_required
def client_job_posting_applicants(request, pk):
    job_posting = get_object_or_404(JobPosting, pk=pk, client__user=request.user)
    applications = job_posting.applications.select_related('freelancer__user')
    return render(request, 'applications/client_job_posting_applicants.html', {
        'job_posting': job_posting,
        'applications': applications,
    })


@login_required
def admin_all_applications(request):
    applications = JobApplication.objects.select_related('job_posting', 'freelancer__user')
    return render(request, 'applications/admin_all_applications.html', {
        'applications': applications,
    })


@login_required
def job_posting_list(request):
    queryset = JobPosting.objects.all()
    q = request.GET.get('q')
    remote = request.GET.get('remote')
    sort_by = request.GET.get('sort_by', '-created_at')  # default newest first

    if q:
        queryset = queryset.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        )

    if remote == 'yes':
        queryset = queryset.filter(is_remote=True)
    elif remote == 'no':
        queryset = queryset.filter(is_remote=False)

    allowed_sort_fields = ['created_at', '-created_at', 'salary_min', '-salary_min', 'salary_max', '-salary_max']
    if sort_by not in allowed_sort_fields:
        sort_by = '-created_at'

    queryset = queryset.order_by(sort_by)

    paginator = Paginator(queryset, 6)  # 6 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'job_postings': page_obj,
        'page_obj': page_obj,
        'q': q,
        'remote': remote,
        'sort_by': sort_by,
    }
    return render(request, 'applications/job_posting_list.html', context)


@login_required
def job_posting_detail(request, pk):
    job_posting = get_object_or_404(JobPosting, pk=pk)
    return render(request, 'applications/job_posting_detail.html', {'job_posting': job_posting})


@login_required
def add_job_posting(request):
    if not hasattr(request.user, 'clientprofile'):
        return redirect('job_posting_list')

    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job_posting = form.save(commit=False)
            job_posting.client = request.user.clientprofile
            job_posting.save()
            messages.success(request, "Job posting added successfully.")
            return redirect('job_posting_detail', pk=job_posting.pk)
    else:
        form = JobPostingForm()

    return render(request, 'applications/job_posting_form.html', {'form': form, 'title': 'Add Job Posting'})


@login_required
def edit_job_posting(request, pk):
    job_posting = get_object_or_404(JobPosting, pk=pk, client=request.user.clientprofile)
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job_posting)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job posting updated successfully.')
            return redirect('job_posting_detail', pk=job_posting.pk)
    else:
        form = JobPostingForm(instance=job_posting)
    return render(request, 'applications/edit_job_posting.html', {'form': form, 'job_posting': job_posting})


@login_required
def delete_job_posting(request, pk):
    job_posting = get_object_or_404(JobPosting, pk=pk, client=request.user.clientprofile)
    if request.method == 'POST':
        job_posting.delete()
        messages.success(request, 'Job posting deleted successfully.')
        return redirect('job_posting_list')
    return render(request, 'applications/confirm_delete_job_posting.html', {'job_posting': job_posting})


def custom_logout(request):
    logout(request)
    return redirect('login')


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


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
def dashboard(request):
    user = request.user

    if hasattr(user, 'clientprofile'):
        context = {
            'profile': user.clientprofile,
        }
        template = 'applications/client_dashboard.html'

    elif hasattr(user, 'freelancerprofile'):
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
        messages.warning(request, "Profile data not found.")
        return redirect('profile')

    return render(request, template, context)


@login_required
def job_list(request):
    user = request.user
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

            # Send notification to client if linked to a job posting
            if application.job_posting and application.job_posting.client:
                client_email = application.job_posting.client.user.email
                freelancer_name = user.username
                send_application_notification(client_email, application.job_posting.title, freelancer_name)

            messages.success(request, 'Application added successfully!')
            return redirect('job_list')
    else:
        form = JobApplicationForm(user=user)

    return render(request, 'applications/application_form.html', {
        'form': form,
        'title': 'Add New Application'
    })


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


class ApplicationDeleteView(DeleteView):
    model = JobApplication
    success_url = reverse_lazy('job_list')
    template_name = 'applications/confirm_delete.html'

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'freelancerprofile'):
            return JobApplication.objects.none()
        return super().get_queryset().filter(user=user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Application deleted successfully.')
        return super().delete(request, *args, **kwargs)


@login_required
def export_applications_csv(request):
    user = request.user
    if not hasattr(user, 'freelancerprofile'):
        messages.error(request, "Access denied: This action is for freelancers only.")
        return redirect('dashboard')

    applications = JobApplication.objects.filter(user=user).order_by('-applied_date')

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
