from django.urls import path
from django.contrib.auth import views as auth_views
from applications import views
urlpatterns = [
    path('export/csv/', views.export_applications_csv, name='export_applications_csv'),
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
