from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

class Company(models.Model):
    """
    Represents a company where the user applied for a job.
    """
    name = models.CharField(max_length=100, unique=True)
    website = models.URLField(blank=True)
    glassdoor_rating = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Tags to categorize job applications (e.g., 'Django', 'Remote', 'Urgent').
    """
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class JobApplication(models.Model):
    """
    Tracks individual job applications for users.
    """
    STATUS_CHOICES = [
        ('AP', 'Applied'),
        ('HR', 'HR Interview'),
        ('TT', 'Technical Test'),
        ('IN', 'Interviewing'),
        ('OF', 'Offer Received'),
        ('RJ', 'Rejected'),
        ('AC', 'Accepted'),
    ]

    SOURCE_CHOICES = [
        ('LN', 'LinkedIn'),
        ('IN', 'Indeed'),
        ('GH', 'GitHub'),
        ('WS', 'Company Website'),
        ('RF', 'Referral'),
        ('OT', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='applications')
    position = models.CharField(max_length=100)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='AP', db_index=True)
    source = models.CharField(max_length=2, choices=SOURCE_CHOICES, blank=True)
    applied_date = models.DateField(db_index=True)
    notes = models.TextField(blank=True, default='')
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    is_remote = models.BooleanField(default=False, db_index=True)
    referral_contact = models.CharField(max_length=100, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="applications")

    class Meta:
        ordering = ['-applied_date']

    def get_absolute_url(self):
        return reverse('application_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.company.name} - {self.position}"


class Interview(models.Model):
    """
    Represents interviews related to a specific job application.
    """
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='interviews')
    interview_type = models.CharField(max_length=100)  # e.g., 'Phone Screen', 'Technical Interview'
    interviewer = models.CharField(max_length=100, blank=True)
    date = models.DateTimeField()
    notes = models.TextField(blank=True)
    follow_up = models.BooleanField(default=False)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.application.position} - {self.interview_type} ({self.date.strftime('%Y-%m-%d %H:%M')})"


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return f"Client Profile: {self.user.username}"


class FreelancerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skills = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    portfolio_link = models.URLField(blank=True)

    def __str__(self):
        return f"Freelancer Profile: {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if hasattr(instance, 'is_client') and instance.is_client:
            ClientProfile.objects.create(user=instance)
        elif hasattr(instance, 'is_freelancer') and instance.is_freelancer:
            FreelancerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'clientprofile'):
        instance.clientprofile.save()
    if hasattr(instance, 'freelancerprofile'):
        instance.freelancerprofile.save()
