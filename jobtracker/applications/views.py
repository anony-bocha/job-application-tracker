from .models import JobApplication
from django.contrib.auth.decorators import login_required  # Add this import
from django.shortcuts import render, redirect
from .forms import JobApplicationForm
from django.shortcuts import get_object_or_404
@login_required
def job_list(request):
    jobs = JobApplication.objects.filter(user=request.user)
    status_filter = request.GET.get('status')
    if status_filter:
        jobs = jobs.filter(status=status_filter)
    return render(request, 'applications/job_list.html', {'jobs': jobs})

def add_application(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            return redirect('job_list')
    else:
        form = JobApplicationForm()
    return render(request, 'applications/add_application.html', {'form': form})


@login_required
def edit_application(request, pk):
    application = get_object_or_404(JobApplication, pk=pk, user=request.user)  # Secure: user can only edit their own apps
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            return redirect('job_list')
    else:
        form = JobApplicationForm(instance=application)
    return render(request, 'applications/edit_application.html', {'form': form})

@login_required
def delete_application(request, pk):
    application = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if request.method == 'POST':
        application.delete()
        return redirect('job_list')
    return render(request, 'applications/confirm_delete.html', {'application': application})