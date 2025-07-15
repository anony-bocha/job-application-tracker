from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('add/', views.add_application, name='add_application'),
    path('edit/<int:pk>/', views.edit_application, name='edit_application'),
    path('delete/<int:pk>/', views.delete_application, name='delete_application'),
]