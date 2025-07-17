from django.urls import path
from django.contrib.auth import views as auth_views
from applications import views

urlpatterns = [
    # Job application views
    path('', views.job_list, name='job_list'),
    path('add/', views.add_application, name='add_application'),
    path('<int:pk>/edit/', views.edit_application, name='edit_application'),
    path('<int:pk>/delete/', views.ApplicationDeleteView.as_view(), name='delete_application'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),

    # Authentication URLs
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login'
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='login'),  # Redirect to login after logout
        name='logout'
    ),
]
