from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from .models import JobListing
from .comprehensive_scraper import ComprehensiveJobScraper
from .google_sheets_integration import GoogleSheetsManager
from .forms import SingleScrapeForm


@login_required
def single_page(request):
    """Single page with scraping form and job listings"""
    from django.core.paginator import Paginator
    
    # Initialize the form
    form = SingleScrapeForm()
    
    job_listings = JobListing.objects.all().order_by('-last_updated')
    
    # Add pagination
    paginator = Paginator(job_listings, 50)  # Show 50 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Process job listings to split decision maker names
    processed_jobs = []
    for job in page_obj:
        job_dict = {
            'job': job,
            'first_name': '',
            'last_name': '',
            'decision_maker': None
        }
        
        # Get first decision maker and split name
        decision_maker = job.company.decision_makers.first() if job.company.decision_makers.exists() else None
        if decision_maker:
            name_parts = decision_maker.decision_maker_name.split(' ', 1)
            job_dict['first_name'] = name_parts[0] if name_parts else ''
            job_dict['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
            job_dict['decision_maker'] = decision_maker
        
        processed_jobs.append(job_dict)
    
    return render(request, 'dashboard/simple_dashboard.html', {
        'processed_jobs': processed_jobs,
        'page_obj': page_obj,
        'form': form
    })


@login_required
@require_POST
def single_scrape(request):
    """Handle scraping from single page"""
    try:
        form = SingleScrapeForm(request.POST)
        
        if form.is_valid():
            keyword_type = form.cleaned_data['keyword_type']
            keywords = form.cleaned_data['keywords']
            job_board = form.cleaned_data['job_board']
            market = form.cleaned_data['market']
            job_type = form.cleaned_data['job_type']
            time_range = form.cleaned_data['time_range']

            # Determine if technical or non-technical
            is_technical = keyword_type == 'Technical'
            
            # Create scraper and run
            scraper = ComprehensiveJobScraper()
            
            # Determine markets to scrape
            markets_to_scrape = []
            if market == 'Both':
                markets_to_scrape = ['USA', 'UK']
            else:
                markets_to_scrape = [market]
            
            total_jobs_scraped = 0
            
            # Scrape for each market
            for current_market in markets_to_scrape:
                jobs_data = scraper.scrape_jobs(
                    keywords=keywords,
                    market=current_market,
                    job_type=job_type.lower().replace('-', '_') if job_type != 'All' else 'full_time',
                    is_technical=is_technical,
                    hours_back=int(time_range),
                    selected_portal=job_board  # Pass the selected portal
                )
                total_jobs_scraped += jobs_data  # jobs_data is the count, not a list

            if total_jobs_scraped > 0:
                messages.success(request, f'Successfully scraped {total_jobs_scraped} {keyword_type.lower()} jobs from {len(markets_to_scrape)} market(s)!')
            else:
                messages.warning(request, 'No jobs found with the specified criteria. Try adjusting your keywords or filters.')
        else:
            # Form validation failed
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
        
    except Exception as e:
        messages.error(request, f'Error during scraping: {str(e)}')
    
    return redirect('dashboard:single-page')


@login_required
def single_export(request):
    """Export jobs to Excel with proper tabs and categorization"""
    try:
        from .excel_export import ExcelExporter
        
        exporter = ExcelExporter()
        
        # Try Excel export first
        try:
            return exporter.export_to_excel()
        except Exception as e:
            # Fallback to CSV if Excel fails
            messages.warning(request, f'Excel export failed, using CSV format: {str(e)}')
            return exporter.export_to_csv()
            
    except Exception as e:
        messages.error(request, f'Export failed: {str(e)}')
        return redirect('dashboard:single-page')


@login_required
@require_POST
def single_save_to_sheet(request):
    """Save jobs to Google Sheet or CSV fallback"""
    try:
        sheets_manager = GoogleSheetsManager()
        success, message = sheets_manager.save_all_jobs_to_sheet()
        
        # Check if it's a fallback CSV save
        if "CSV file" in message:
            messages.info(request, f"📁 {message}")
        elif success:
            messages.success(request, f"✅ {message}")
        else:
            messages.error(request, f"❌ {message}")
        
        return JsonResponse({
            'success': success,
            'message': message
        })
    except Exception as e:
        error_msg = f'Error saving to Google Sheet: {str(e)}'
        messages.error(request, f"❌ {error_msg}")
        return JsonResponse({
            'success': False,
            'message': error_msg
        })


@login_required
@require_POST
def single_delete_all(request):
    """Delete all jobs, companies, and decision makers"""
    try:
        from .models import Company, DecisionMaker
        
        # Delete all related data
        JobListing.objects.all().delete()
        DecisionMaker.objects.all().delete()
        Company.objects.all().delete()
        
        messages.success(request, 'All data deleted successfully!')
        return redirect('dashboard:single-page')
    except Exception as e:
        messages.error(request, f'Error deleting data: {str(e)}')
        return redirect('dashboard:single-page')


@login_required
@require_POST
def single_delete_job(request, job_id):
    """Delete a single job"""
    try:
        job = JobListing.objects.get(id=job_id)
        job.delete()
        return redirect('dashboard:single-page')
    except JobListing.DoesNotExist:
        messages.error(request, 'Job not found!')
        return redirect('dashboard:single-page')
    except Exception as e:
        messages.error(request, f'Error deleting job: {str(e)}')
        return redirect('dashboard:single-page')


@login_required
def single_edit_job(request, job_id):
    """Edit a single job listing"""
    try:
        job = JobListing.objects.get(id=job_id)
        decision_maker = job.company.decision_makers.first() if job.company.decision_makers.exists() else None
        
        if request.method == 'POST':
            # Update job data
            job.job_title = request.POST.get('job_title', job.job_title)
            job.location = request.POST.get('location', job.location)
            job.company_size = request.POST.get('company_size', job.company_size)
            job.is_technical = request.POST.get('is_technical') == 'on'
            
            # Update company data
            job.company.name = request.POST.get('company_name', job.company.name)
            job.company.company_url = request.POST.get('company_url', job.company.company_url)
            job.company.save()
            
            # Update decision maker data
            if decision_maker:
                decision_maker.decision_maker_name = request.POST.get('decision_maker_name', decision_maker.decision_maker_name)
                decision_maker.decision_maker_title = request.POST.get('decision_maker_title', decision_maker.decision_maker_title)
                decision_maker.decision_maker_email = request.POST.get('decision_maker_email', decision_maker.decision_maker_email)
                decision_maker.decision_maker_phone = request.POST.get('decision_maker_phone', decision_maker.decision_maker_phone)
                decision_maker.decision_maker_linkedin = request.POST.get('decision_maker_linkedin', decision_maker.decision_maker_linkedin)
                decision_maker.save()
            
            job.save()
            messages.success(request, 'Job listing updated successfully!')
            return redirect('dashboard:single-page')
        
        return render(request, 'dashboard/edit_job.html', {
            'job': job,
            'decision_maker': decision_maker
        })
        
    except JobListing.DoesNotExist:
        messages.error(request, 'Job listing not found!')
        return redirect('dashboard:single-page')
    except Exception as e:
        messages.error(request, f'Error editing job: {str(e)}')
        return redirect('dashboard:single-page')
