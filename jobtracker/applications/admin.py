from django.contrib import admin
from .models import Company, JobApplication, Interview
from .models import Tag
from .models import ClientProfile, FreelancerProfile
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('company', 'position', 'status', 'user', 'applied_date', 'is_remote')
    list_filter = ('status', 'applied_date', 'is_remote', 'source', 'company')
    search_fields = ('position', 'company__name', 'user__username')
    ordering = ('-applied_date',)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'glassdoor_rating')
    search_fields = ('name',)

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'interview_type', 'date', 'interviewer', 'follow_up')
    list_filter = ('date', 'follow_up', 'interview_type')
    search_fields = ('application__position', 'interviewer')
    ordering = ('-date',)


admin.site.register(ClientProfile)
admin.site.register(FreelancerProfile)