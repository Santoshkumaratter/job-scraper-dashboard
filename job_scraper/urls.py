"""
URL configuration for job_scraper project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from dashboard.views import RegisterView, CustomLoginView
from dashboard.home_views import home_page

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # Authentication
    path('accounts/register/', 
         RegisterView.as_view(), 
         name='register'),
    path('accounts/login/', 
         CustomLoginView.as_view(
             template_name='registration/login.html',
             redirect_authenticated_user=True
         ), 
         name='login'),
    path('accounts/logout/', 
         auth_views.LogoutView.as_view(
             next_page='home',
             template_name='registration/logged_out.html'
         ), 
         name='logout'),
    path('accounts/password_change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='registration/password_change_form.html',
             success_url=reverse_lazy('dashboard:home')
         ), 
         name='password_change'),
    path('accounts/password_change/done/', 
         auth_views.PasswordChangeDoneView.as_view(
             template_name='registration/password_change_done.html'
         ), 
         name='password_change_done'),
    
    # Home page
    path('', home_page, name='home'),
    
    # Dashboard app
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin site customizations
admin.site.site_header = 'Job Scraper Admin'
admin.site.site_title = 'Job Scraper Administration'
admin.site.index_title = 'Welcome to Job Scraper Admin'
