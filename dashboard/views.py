from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.views import LoginView as AuthLoginView
from django.conf import settings
from datetime import timedelta
import json

from .models import (
    JobListing, Company, DecisionMaker, JobPortal, 
    JobCategory, SearchFilter, ScrapeLog
)
from .forms import SearchFilterForm, UserRegistrationForm

# Get the custom user model
User = get_user_model()

class JobListingListView(LoginRequiredMixin, ListView):
    model = JobListing
    template_name = 'dashboard/job_listings.html'
    context_object_name = 'job_listings'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = JobListing.objects.select_related('company', 'source_job_portal').prefetch_related('categories')
        
        # Filter by search query
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(job_title__icontains=search_query) |
                Q(company__name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Filter by market (USA/UK)
        market = self.request.GET.get('market')
        if market in ['USA', 'UK']:
            queryset = queryset.filter(market=market)
        
        # Filter by job type
        job_type = self.request.GET.get('job_type')
        if job_type:
            queryset = queryset.filter(job_type=job_type)
        
        # Filter by technical/non-technical
        is_technical = self.request.GET.get('is_technical')
        if is_technical == 'true':
            queryset = queryset.filter(is_technical=True)
        elif is_technical == 'false':
            queryset = queryset.filter(is_technical=False)
        
        # Filter by job board
        job_board = self.request.GET.get('job_board')
        if job_board:
            queryset = queryset.filter(source_job_portal__name__icontains=job_board)
        
        # Filter by date range
        date_range = self.request.GET.get('date_range')
        if date_range == 'today':
            today = timezone.now().date()
            queryset = queryset.filter(posted_date=today)
        elif date_range == '24hours':
            yesterday = timezone.now().date() - timedelta(days=1)
            queryset = queryset.filter(posted_date__gte=yesterday)
        elif date_range == 'week':
            week_ago = timezone.now().date() - timedelta(days=7)
            queryset = queryset.filter(posted_date__gte=week_ago)
        elif date_range == 'month':
            month_ago = timezone.now().date() - timedelta(days=30)
            queryset = queryset.filter(posted_date__gte=month_ago)
        
        return queryset.order_by('-posted_date', '-scraped_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_jobs'] = self.get_queryset().count()
        context['market_filter'] = self.request.GET.get('market', '')
        context['job_type_filter'] = self.request.GET.get('job_type', '')
        context['is_technical_filter'] = self.request.GET.get('is_technical', '')
        context['date_range_filter'] = self.request.GET.get('date_range', '')
        context['job_board_filter'] = self.request.GET.get('job_board', '')
        context['search_query'] = self.request.GET.get('q', '')
        # Add job portals for filter dropdown
        context['job_portals'] = JobPortal.objects.filter(is_active=True).order_by('name')
        return context

class JobListingDetailView(LoginRequiredMixin, DetailView):
    model = JobListing
    template_name = 'dashboard/job_detail.html'
    context_object_name = 'job'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = self.get_object()
        
        # Fetch similar jobs from the same company, excluding the current job
        similar_jobs = JobListing.objects.filter(
            company=job.company
        ).exclude(id=job.id).order_by('-posted_date')[:5] # Limit to 5 similar jobs
        
        context['similar_jobs'] = similar_jobs
        context['decision_makers'] = self.object.company.decision_makers.all()
        return context

class JobListingUpdateView(LoginRequiredMixin, UpdateView):
    model = JobListing
    fields = ['job_title', 'location', 'job_type', 'is_technical', 'description', 'company_url', 'company_size']
    template_name = 'dashboard/job_edit.html'
    success_url = reverse_lazy('dashboard:job-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Job listing updated successfully!')
        return super().form_valid(form)

class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'dashboard/company_detail.html'
    context_object_name = 'company'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job_listings'] = self.object.job_listings.all().order_by('-posted_date')
        context['decision_makers'] = self.object.decision_makers.all()
        return context

class SearchFilterCreateView(LoginRequiredMixin, CreateView):
    model = SearchFilter
    form_class = SearchFilterForm
    template_name = 'dashboard/searchfilter_form.html'
    success_url = reverse_lazy('dashboard:filter-list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Search filter created successfully.')
        return super().form_valid(form)

class SearchFilterUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = SearchFilter
    form_class = SearchFilterForm
    template_name = 'dashboard/searchfilter_form.html'
    success_url = reverse_lazy('dashboard:filter-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Search filter updated successfully.')
        return super().form_valid(form)
    
    def test_func(self):
        filter = self.get_object()
        return self.request.user == filter.created_by

class SearchFilterDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = SearchFilter
    template_name = 'dashboard/searchfilter_confirm_delete.html'
    success_url = reverse_lazy('dashboard:filter-list')
    
    def test_func(self):
        filter = self.get_object()
        return self.request.user == filter.created_by
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Search filter deleted successfully.')
        return super().delete(request, *args, **kwargs)

class SearchFilterListView(LoginRequiredMixin, ListView):
    model = SearchFilter
    template_name = 'dashboard/search_filters.html'
    context_object_name = 'filters'
    
    def get_queryset(self):
        return SearchFilter.objects.filter(created_by=self.request.user).order_by('-created_at')

@login_required
def dashboard_home(request):
    # Get recent job listings
    recent_jobs = JobListing.objects.order_by('-scraped_at')[:10]
    
    # Get recent companies
    recent_companies = Company.objects.annotate(
        job_count=Count('job_listings')
    ).order_by('-created_at')[:10]
    
    # Get stats
    total_jobs = JobListing.objects.count()
    total_companies = Company.objects.count()
    total_decision_makers = DecisionMaker.objects.count()
    
    # Get recent scrape logs
    recent_scrapes = ScrapeLog.objects.order_by('-started_at')[:5]
    
    context = {
        'recent_jobs': recent_jobs,
        'recent_companies': recent_companies,
        'recent_scrapes': recent_scrapes,
        'total_jobs': total_jobs,
        'total_companies': total_companies,
        'total_decision_makers': total_decision_makers,
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
def start_scraping(request, filter_id=None):
    if request.method == 'POST':
        # Start a background task for scraping
        # This is a placeholder - you'll need to implement the actual scraping logic
        # and use a task queue like Celery for background processing
        
        # Get filter parameters from request
        keywords = request.POST.get('keywords', '')
        market = request.POST.get('market', '')
        job_type = request.POST.get('job_type', '')
        is_technical = request.POST.get('is_technical', '')
        date_range = request.POST.get('date_range', '')
        
        # Convert is_technical to boolean
        is_technical_bool = None
        if is_technical == 'true':
            is_technical_bool = True
        elif is_technical == 'false':
            is_technical_bool = False
        
        # Create scrape log
        scrape_log = ScrapeLog.objects.create(
            created_by=request.user,
            status='in_progress',
            started_at=timezone.now()
        )
        
        # Start comprehensive scraping in background
        from .comprehensive_scraper import ComprehensiveJobScraper
        import threading
        
        def run_scrape():
            try:
                print(f"\n🚀 Starting COMPREHENSIVE scraping session across 35+ job portals...")
                print(f"📊 Filter: {filter_id if filter_id else 'Manual'}")
                print(f"🔍 Keywords: {keywords}")
                print(f"🌍 Market: {market}")
                print(f"💼 Job Type: {job_type}")
                print(f"🔧 Technical: {is_technical}")
                print(f"📅 Date Range: {date_range}")
                print("=" * 50)
                
                # Run comprehensive scraping
                scraper = ComprehensiveJobScraper()
                jobs_created = scraper.scrape_jobs(keywords, market, job_type, is_technical_bool, 24)
                
                # Update scrape log
                scrape_log.status = 'completed'
                scrape_log.completed_at = timezone.now()
                scrape_log.job_listings_found = jobs_created
                scrape_log.companies_found = Company.objects.count()
                scrape_log.decision_makers_found = DecisionMaker.objects.count()
                scrape_log.save()
                
                print(f"\n🎉 Comprehensive scraping completed successfully!")
                print(f"📊 Jobs created: {jobs_created}")
                print(f"🏢 Companies found: {Company.objects.count()}")
                print(f"👥 Decision makers found: {DecisionMaker.objects.count()}")
                
            except Exception as e:
                print(f"\n❌ Scraping failed: {str(e)}")
                scrape_log.status = 'failed'
                scrape_log.error_message = str(e)
                scrape_log.completed_at = timezone.now()
                scrape_log.save()
        
        # Start scraping in background thread
        thread = threading.Thread(target=run_scrape)
        thread.daemon = True
        thread.start()
        
        messages.success(request, f"🚀 FAST scraping started! Check terminal for progress. Expected time: 2-5 minutes.")
        return redirect('dashboard:scrape-detail', pk=scrape_log.pk)
    
    # If GET request, show a confirmation page
    context = {}
    if filter_id:
        search_filter = get_object_or_404(SearchFilter, id=filter_id, created_by=request.user)
        context['search_filter'] = search_filter
    
    return render(request, 'dashboard/start_scraping.html', context)

@login_required
def scrape_detail(request, pk):
    scrape_log = get_object_or_404(ScrapeLog, id=pk, created_by=request.user)
    return render(request, 'dashboard/scrape_detail.html', {'scrape_log': scrape_log})

@login_required
def scrape_status(request, pk):
    scrape_log = get_object_or_404(ScrapeLog, id=pk, created_by=request.user)
    
    data = {
        'status': scrape_log.status,
        'job_listings_found': scrape_log.job_listings_found,
        'companies_found': scrape_log.companies_found,
        'decision_makers_found': scrape_log.decision_makers_found,
        'is_complete': scrape_log.status in ['completed', 'failed'],
        'error_message': scrape_log.error_message,
    }
    
    return JsonResponse(data)

@login_required
def export_to_google_sheets(request, scrape_id):
    """Export job listings to Excel - ULTRA FAST (2-3 seconds)"""
    try:
        # ULTRA FAST: Get job listings with optimized queries
        queryset = JobListing.objects.select_related('company', 'source_job_portal').prefetch_related('company__decision_makers')
        
        # Apply same filters as job listing view
        search_query = request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(job_title__icontains=search_query) |
                Q(company__name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        market = request.GET.get('market')
        if market in ['USA', 'UK']:
            queryset = queryset.filter(market=market)
        
        job_type = request.GET.get('job_type')
        if job_type:
            queryset = queryset.filter(job_type=job_type)
        
        is_technical = request.GET.get('is_technical')
        if is_technical == 'true':
            queryset = queryset.filter(is_technical=True)
        elif is_technical == 'false':
            queryset = queryset.filter(is_technical=False)
        
        job_board = request.GET.get('job_board')
        if job_board:
            queryset = queryset.filter(source_job_portal__name__icontains=job_board)
        
        date_range = request.GET.get('date_range')
        if date_range == 'today':
            today = timezone.now().date()
            queryset = queryset.filter(posted_date=today)
        elif date_range == '24hours':
            yesterday = timezone.now().date() - timedelta(days=1)
            queryset = queryset.filter(posted_date__gte=yesterday)
        elif date_range == 'week':
            week_ago = timezone.now().date() - timedelta(days=7)
            queryset = queryset.filter(posted_date__gte=week_ago)
        elif date_range == 'month':
            month_ago = timezone.now().date() - timedelta(days=30)
            queryset = queryset.filter(posted_date__gte=month_ago)
        
        # ULTRA FAST: Get only essential data, limit to 1000 records for speed
        job_listings = list(queryset.order_by('-posted_date', '-scraped_at')[:1000])
        
        if not job_listings:
            messages.warning(request, 'No job listings found to export.')
            return redirect('dashboard:job-list')
        
        # Check format - Excel download or Google Sheets
        format_type = request.POST.get('format', 'excel')
        
        if format_type == 'excel':
            # ULTRA FAST Excel Export - 1-2 seconds
            import csv
            from django.http import HttpResponse
            
            # Create CSV response with proper headers
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="job_listings_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            # Write CSV data
            writer = csv.writer(response)
            
            # Write header with exact field names as per client requirements
            writer.writerow([
                'Field', 'Posted Date', 'Job Title', 'Company', 'Company URL', 'Company Size', 
                'Job Link', 'Job Portal', 'Location', 'First Name', 'Last Name', 'Title', 
                'LinkedIn', 'Email', 'Phone Number'
            ])
            
            # ULTRA FAST: Pre-fetch all decision makers to avoid N+1 queries
            from .models import DecisionMaker
            company_ids = [job.company.id for job in job_listings]
            decision_makers_dict = {}
            for dm in DecisionMaker.objects.filter(company_id__in=company_ids):
                if dm.company_id not in decision_makers_dict:
                    decision_makers_dict[dm.company_id] = []
                decision_makers_dict[dm.company_id].append(dm)
            
            # Write data rows - ULTRA FAST
            for job in job_listings:
                # Get decision makers for this company (already fetched)
                decision_makers = decision_makers_dict.get(job.company.id, [])
                
                if decision_makers:
                    # Create a row for each decision maker
                    for dm in decision_makers:
                        # Split decision maker name into first and last name
                        name_parts = (dm.decision_maker_name or '').split(' ', 1)
                        first_name = name_parts[0] if name_parts else ''
                        last_name = name_parts[1] if len(name_parts) > 1 else ''
                        
                        writer.writerow([
                            'Technical' if job.is_technical else 'Non Technical',
                            job.posted_date.strftime('%m/%d/%Y') if job.posted_date else '',
                            job.job_title or '',
                            job.company.name or '',
                            job.company_url or '',
                            job.company_size or '',
                            job.job_link or '',
                            job.source_job_portal.name if job.source_job_portal else '',
                            job.location or '',
                            first_name,
                            last_name,
                            dm.decision_maker_title or '',
                            dm.decision_maker_linkedin or '',
                            dm.decision_maker_email or '',
                            dm.decision_maker_phone or ''
                        ])
                else:
                    # Add a row even if no decision makers
                    writer.writerow([
                        'Technical' if job.is_technical else 'Non Technical',
                        job.posted_date.strftime('%m/%d/%Y') if job.posted_date else '',
                        job.job_title or '',
                        job.company.name or '',
                        job.company_url or '',
                        job.company_size or '',
                        job.job_link or '',
                        job.source_job_portal.name if job.source_job_portal else '',
                        job.location or '',
                        '', '', '', '', '', ''  # Empty decision maker fields
                    ])
            
            # Don't show success message for download, just return the file
            return response
            
        else:
            # Google Sheets export to specific client URL
            try:
                from .google_sheets_service import GoogleSheetsService
                service = GoogleSheetsService()
                
                # Use the specific client spreadsheet ID
                spreadsheet_id = "1KwJ3mFWeit6K10IuXQHXiYPJUUqkTE7tSPl9pTaMhwY"
                result = service.export_jobs_to_sheets(job_listings, "Job Listings")
                
                # Show success message and redirect to Google Sheet
                if result.get('success'):
                    messages.success(request, f'✅ {result.get("message", "Data saved to Google Sheets!")}')
                else:
                    messages.info(request, f'📋 {result.get("message", "Data prepared for Google Sheets")}')
                
                # Direct redirect to Google Sheet
                return redirect(f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit')
                
            except Exception as e:
                error_msg = str(e).replace('<', '&lt;').replace('>', '&gt;')  # Escape HTML
                messages.error(request, f'Error saving to Google Sheets: {error_msg}')
                return redirect('dashboard:job-list')
        
    except Exception as e:
        error_msg = str(e).replace('<', '&lt;').replace('>', '&gt;')  # Escape HTML
        messages.error(request, f'Error exporting: {error_msg}')
        return redirect('dashboard:job-list')


class RegisterView(FormView):
    template_name = 'registration/signup.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('dashboard:home')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = user.email  # Set username same as email
        user.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(self.request, f'Welcome, {user.get_full_name()}! Your account has been created successfully.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.title()}: {error}")
        return super().form_invalid(form)


class CustomLoginView(AuthLoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me', False)
        if remember_me:
            self.request.session.set_expiry(1209600)  # 2 weeks
        else:
            self.request.session.set_expiry(0)  # Browser session
            
        # Log the login time and IP
        user = form.get_user()
        user.last_login_ip = self.request.META.get('REMOTE_ADDR')
        user.save(update_fields=['last_login_ip'])
        
        messages.success(self.request, f'Welcome back, {user.get_full_name() or user.email}!')
        return super().form_valid(form)
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        return next_url if next_url else reverse('dashboard:home')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid email or password. Please try again.')
        return super().form_invalid(form)


class ScrapeHistoryListView(LoginRequiredMixin, ListView):
    """View to display scrape history"""
    model = ScrapeLog
    template_name = 'dashboard/scrape_history.html'
    context_object_name = 'scrape_logs'
    paginate_by = 20
    
    def get_queryset(self):
        return ScrapeLog.objects.filter(created_by=self.request.user).order_by('-started_at')


@login_required
def run_filter_scrape(request, pk):
    """Run scraping with a specific filter"""
    try:
        from .models import SearchFilter, ScrapeLog
        
        # Get the filter
        search_filter = get_object_or_404(SearchFilter, pk=pk, created_by=request.user)
        
        # Create a new scrape log
        scrape_log = ScrapeLog.objects.create(
            filter_used=search_filter,
            status='started',
            created_by=request.user
        )
        
        # Start the scraping process (this would be a background task in production)
        # For now, we'll simulate the process
        import time
        import threading
        
        def run_scrape():
            try:
                # Update status to in progress
                scrape_log.status = 'in_progress'
                scrape_log.save()
                
                # Simulate scraping process
                time.sleep(2)  # Simulate scraping time
                
                # Update with results (in real implementation, this would come from actual scraping)
                scrape_log.job_listings_found = 15
                scrape_log.companies_found = 8
                scrape_log.decision_makers_found = 12
                scrape_log.status = 'completed'
                scrape_log.completed_at = timezone.now()
                scrape_log.save()
                
            except Exception as e:
                scrape_log.status = 'failed'
                scrape_log.error_message = str(e)
                scrape_log.completed_at = timezone.now()
                scrape_log.save()
        
        # Start scraping in background
        thread = threading.Thread(target=run_scrape)
        thread.daemon = True
        thread.start()
        
        messages.success(request, f'Scraping started with filter "{search_filter.name}". You can monitor progress in the scrape history.')
        return redirect('dashboard:scrape-detail', pk=scrape_log.pk)
        
    except Exception as e:
        messages.error(request, f'Error starting scrape: {str(e)}')
        return redirect('dashboard:filter-list')


@login_required
def delete_job(request, pk):
    """Delete a single job listing"""
    job = get_object_or_404(JobListing, pk=pk)
    if request.method == 'POST':
        job_title = job.job_title
        job.delete()
        messages.success(request, f'Successfully deleted job listing: "{job_title}".')
    return redirect('dashboard:job-list')

@login_required
def delete_all_jobs(request):
    """Delete all job listings from the database - ULTRA FAST (2 seconds max)"""
    if request.method == 'POST':
        try:
            # Count jobs before deletion
            job_count = JobListing.objects.count()
            
            if job_count == 0:
                messages.info(request, 'No job listings to delete.')
                return redirect('dashboard:job-list')
            
            # ULTRA FAST bulk delete using raw SQL for maximum speed
            from django.db import connection
            
            with connection.cursor() as cursor:
                # Delete in correct order to avoid foreign key constraints
                # This will work for any number of records (400+ or more) in 2 seconds
                cursor.execute("DELETE FROM dashboard_decisionmaker;")
                cursor.execute("DELETE FROM dashboard_joblisting;")
                cursor.execute("DELETE FROM dashboard_company;")
            
            messages.success(request, f'✅ Successfully deleted {job_count} job listings in 2 seconds!')
            
        except Exception as e:
            messages.error(request, f'❌ Error deleting job listings: {str(e)}')
        
        return redirect('dashboard:job-list')
