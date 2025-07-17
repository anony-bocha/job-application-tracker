from django.contrib import admin
from .models import Company, JobApplication

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('company', 'position', 'status', 'user')
    list_filter = ('status', 'applied_date')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'glassdoor_rating')
