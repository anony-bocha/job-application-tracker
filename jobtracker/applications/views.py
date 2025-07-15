from django.shortcuts import render
from .models import JobApplication
from django.contrib.auth.decorators import login_required  # Add this import

@login_required  # This ensures only logged-in users can access
def job_list(request):
    jobs = JobApplication.objects.filter(user=request.user)  # Now this will work
    return render(request, 'applications/job_list.html', {'jobs': jobs})