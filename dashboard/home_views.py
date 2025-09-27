from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import JobListing, Company, DecisionMaker


@login_required
def home_page(request):
    """Home page with user info and stats"""
    # Get statistics
    total_jobs = JobListing.objects.count()
    total_companies = Company.objects.count()
    total_decision_makers = DecisionMaker.objects.count()
    
    return render(request, 'home.html', {
        'total_jobs': total_jobs,
        'total_companies': total_companies,
        'total_decision_makers': total_decision_makers,
    })
