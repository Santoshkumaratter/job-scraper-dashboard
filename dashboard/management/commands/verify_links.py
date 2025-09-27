#!/usr/bin/env python
"""
Quick verification of link formats and sample data
"""

from django.core.management.base import BaseCommand
from dashboard.models import JobListing, Company, DecisionMaker

class Command(BaseCommand):
    help = 'Quick verification of link formats and sample data'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('📋 Verifying link formats and sample data...')
        )
        
        # Show sample job data
        self.show_sample_jobs()
        
        # Show sample company data
        self.show_sample_companies()
        
        # Show sample decision maker data
        self.show_sample_decision_makers()
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ Link verification completed!')
        )
    
    def show_sample_jobs(self):
        """Show sample job data with links"""
        self.stdout.write(f'\n🔗 Sample Job Links:')
        
        jobs = JobListing.objects.select_related('company', 'source_job_portal')[:5]
        
        for i, job in enumerate(jobs, 1):
            self.stdout.write(f'\n{i}. {job.job_title} at {job.company.name}')
            self.stdout.write(f'   Portal: {job.source_job_portal.name if job.source_job_portal else "N/A"}')
            self.stdout.write(f'   Posted: {job.posted_date}')
            self.stdout.write(f'   Location: {job.location}')
            self.stdout.write(f'   Technical: {"Yes" if job.is_technical else "No"}')
            self.stdout.write(f'   Job Link: {job.job_link}')
    
    def show_sample_companies(self):
        """Show sample company data"""
        self.stdout.write(f'\n🏢 Sample Company URLs:')
        
        companies = Company.objects.all()[:5]
        
        for i, company in enumerate(companies, 1):
            self.stdout.write(f'\n{i}. {company.name}')
            self.stdout.write(f'   URL: {company.url}')
            self.stdout.write(f'   Size: {company.company_size}')
            self.stdout.write(f'   Industry: {company.industry}')
    
    def show_sample_decision_makers(self):
        """Show sample decision maker data"""
        self.stdout.write(f'\n👥 Sample Decision Makers:')
        
        decision_makers = DecisionMaker.objects.select_related('company')[:10]
        
        for i, dm in enumerate(decision_makers, 1):
            self.stdout.write(f'\n{i}. {dm.decision_maker_name}')
            self.stdout.write(f'   Title: {dm.decision_maker_title}')
            self.stdout.write(f'   Company: {dm.company.name}')
            self.stdout.write(f'   Email: {dm.decision_maker_email}')
            self.stdout.write(f'   Phone: {dm.decision_maker_phone}')
            self.stdout.write(f'   LinkedIn: {dm.decision_maker_linkedin}')
