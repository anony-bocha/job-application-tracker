from django.contrib import admin
from django.urls import path, include
from applications import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('applications.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # Add this line
]