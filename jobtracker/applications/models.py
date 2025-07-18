from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Company(models.Model):
    name = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    glassdoor_rating = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
class JobApplication(models.Model):
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
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='AP')
    source = models.CharField(max_length=2, choices=SOURCE_CHOICES, blank=True)
    applied_date = models.DateField()
    notes = models.TextField(blank=True, default='')
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    is_remote = models.BooleanField(default=False)
    referral_contact = models.CharField(max_length=100, blank=True)

    def get_absolute_url(self):
        return reverse('application_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.company.name} - {self.position}"

class Interview(models.Model):
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='interviews')
    interview_type = models.CharField(max_length=100)
    interviewer = models.CharField(max_length=100, blank=True)
    date = models.DateTimeField()
    notes = models.TextField(blank=True)
    follow_up = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.application.position} - {self.interview_type} ({self.date.strftime('%Y-%m-%d %H:%M')})"
