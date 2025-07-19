from django.urls import path
from django.contrib.auth import views as auth_views
from applications import views
urlpatterns = [
    path('export/csv/', views.export_applications_csv, name='export_applications_csv'),  
    path('job-postings/<int:pk>/applicants/', views.client_job_posting_applicants, name='client_job_posting_applicants'),
    path('admin/applications/', views.admin_all_applications, name='admin_all_applications'),
    path('job-postings/<int:pk>/delete/', views.delete_job_posting, name='delete_job_posting'),
    path('job-postings/', views.job_posting_list, name='job_posting_list'),
    path('job-postings/add/', views.add_job_posting, name='add_job_posting'),
    path('job-postings/<int:pk>/', views.job_posting_detail, name='job_posting_detail'),
    path('job-postings/<int:pk>/edit/', views.edit_job_posting, name='edit_job_posting'),
    path('', views.job_list, name='job_list'),
    path('add/', views.add_application, name='add_application'),
    path('<int:pk>/edit/', views.edit_application, name='edit_application'),
    path('<int:pk>/delete/', views.ApplicationDeleteView.as_view(), name='delete_application'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
]
