from django.db import models
from django.contrib.auth.models import User  # Add this import

class JobApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Add this line
    company = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default="Applied")
    applied_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.company} - {self.position}"