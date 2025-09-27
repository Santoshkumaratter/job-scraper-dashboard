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


@login_required
def single_page(request):
    """Single page with scraping form and job listings"""
    job_listings = JobListing.objects.all().order_by('-last_updated')
    
    # Process job listings to split decision maker names
    processed_jobs = []
    for job in job_listings:
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
        'processed_jobs': processed_jobs
    })


@login_required
@require_POST
def single_scrape(request):
    """Handle scraping from single page"""
    try:
        keyword_type = request.POST.get('keyword_type', 'Technical')
        keywords = request.POST.get('keywords', '')
        job_board = request.POST.get('job_board', 'All')
        market = request.POST.get('market', 'USA')
        job_type = request.POST.get('job_type', 'All')
        time_range = request.POST.get('time_range', '24')

        # Validate that keywords are provided
        if not keywords.strip():
            messages.error(request, 'Keywords are required!')
            return redirect('dashboard:single-page')

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
                job_type=job_type.lower().replace('-', '_'),
                is_technical=is_technical,
                hours_back=int(time_range)
            )
            total_jobs_scraped += jobs_data  # jobs_data is the count, not a list

        if total_jobs_scraped > 0:
            messages.success(request, f'Successfully scraped {total_jobs_scraped} {keyword_type.lower()} jobs from {len(markets_to_scrape)} market(s)!')
        else:
            messages.warning(request, 'No jobs found with the specified criteria. Try adjusting your keywords or filters.')
        
    except Exception as e:
        messages.error(request, f'Error during scraping: {str(e)}')
    
    return redirect('dashboard:single-page')


@login_required
def single_export(request):
    """Export jobs to Excel"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="job_listings.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Field', 'Posted Date', 'Job Title', 'Company', 'Company URL', 'Company Size',
        'Job Link', 'Job Portal', 'Location', 'First Name', 'Last Name', 'Title',
        'LinkedIn', 'Email', 'Phone Number'
    ])
    
    # Write data
    jobs = JobListing.objects.all().select_related('company', 'source_job_portal').prefetch_related('company__decision_makers')
    
    for job in jobs:
        # Get first decision maker
        decision_maker = job.company.decision_makers.first() if job.company.decision_makers.exists() else None
        
        if decision_maker:
            name_parts = decision_maker.decision_maker_name.split(' ', 1)
            first_name = name_parts[0] if name_parts else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''
        else:
            first_name = last_name = ''
        
        writer.writerow([
            'Technical' if job.is_technical else 'Non-Technical',
            job.posted_date.strftime('%m/%d/%Y') if job.posted_date else '',
            job.job_title,
            job.company.name,
            job.company_url or '',
            job.company_size or '',
            job.job_link or '',
            job.source_job_portal.name if job.source_job_portal else '',
            job.location,
            first_name,
            last_name,
            decision_maker.decision_maker_title if decision_maker else '',
            decision_maker.decision_maker_linkedin if decision_maker else '',
            decision_maker.decision_maker_email if decision_maker else '',
            decision_maker.decision_maker_phone if decision_maker else '',
        ])
    
    return response


@login_required
@require_POST
def single_save_to_sheet(request):
    """Save jobs to Google Sheet"""
    try:
        sheets_manager = GoogleSheetsManager()
        success, message = sheets_manager.save_all_jobs_to_sheet()
        
        return JsonResponse({
            'success': success,
            'message': message
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error saving to Google Sheet: {str(e)}'
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
