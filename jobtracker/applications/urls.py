from django.urls import path
from django.contrib.auth import views as auth_views
from applications import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('add/', views.add_application, name='add_application'),
    path('<int:pk>/edit/', views.edit_application, name='edit_application'),
    path('<int:pk>/delete/', views.delete_application, name='delete_application'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]