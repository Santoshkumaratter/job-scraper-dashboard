#!/usr/bin/env python
"""
Test all links to ensure they open correctly and don't show "not found" errors
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import JobListing, Company, DecisionMaker
import requests
import time
import random

class Command(BaseCommand):
    help = 'Test all links to ensure they open correctly'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔗 Testing all links for validity...')
        )
        
        # Test job links
        self.test_job_links()
        
        # Test company URLs
        self.test_company_urls()
        
        # Test LinkedIn profiles
        self.test_linkedin_profiles()
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Link testing completed!')
        )
    
    def test_job_links(self):
        """Test job links to ensure they're valid"""
        self.stdout.write(f'\n🔗 Testing Job Links...')
        
        jobs_with_links = JobListing.objects.exclude(job_link='')
        total_jobs = jobs_with_links.count()
        
        if total_jobs == 0:
            self.stdout.write('❌ No jobs with links found. Creating test data...')
            self.create_test_data()
            jobs_with_links = JobListing.objects.exclude(job_link='')
            total_jobs = jobs_with_links.count()
        
        self.stdout.write(f'📋 Testing {total_jobs} job links...')
        
        valid_links = 0
        invalid_links = 0
        test_count = min(20, total_jobs)  # Test first 20 links
        
        for i, job in enumerate(jobs_with_links[:test_count]):
            try:
                # Test the link
                response = requests.head(job.job_link, timeout=10, allow_redirects=True)
                
                if response.status_code == 200:
                    valid_links += 1
                    self.stdout.write(f'✅ {job.job_title} - {job.source_job_portal.name if job.source_job_portal else "Unknown"}: {response.status_code}')
                else:
                    invalid_links += 1
                    self.stdout.write(f'❌ {job.job_title} - {job.source_job_portal.name if job.source_job_portal else "Unknown"}: {response.status_code}')
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                invalid_links += 1
                self.stdout.write(f'❌ {job.job_title} - Error: {str(e)[:50]}...')
        
        self.stdout.write(f'\n📊 Job Links Results:')
        self.stdout.write(f'   Valid links: {valid_links}/{test_count}')
        self.stdout.write(f'   Invalid links: {invalid_links}/{test_count}')
        self.stdout.write(f'   Success rate: {valid_links/test_count*100:.1f}%')
    
    def test_company_urls(self):
        """Test company URLs to ensure they're valid"""
        self.stdout.write(f'\n🏢 Testing Company URLs...')
        
        companies_with_urls = Company.objects.exclude(url='')
        total_companies = companies_with_urls.count()
        
        if total_companies == 0:
            self.stdout.write('❌ No companies with URLs found.')
            return
        
        self.stdout.write(f'📋 Testing {total_companies} company URLs...')
        
        valid_urls = 0
        invalid_urls = 0
        test_count = min(15, total_companies)  # Test first 15 URLs
        
        for i, company in enumerate(companies_with_urls[:test_count]):
            try:
                # Test the URL
                response = requests.head(company.url, timeout=10, allow_redirects=True)
                
                if response.status_code == 200:
                    valid_urls += 1
                    self.stdout.write(f'✅ {company.name}: {response.status_code}')
                else:
                    invalid_urls += 1
                    self.stdout.write(f'❌ {company.name}: {response.status_code}')
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                invalid_urls += 1
                self.stdout.write(f'❌ {company.name} - Error: {str(e)[:50]}...')
        
        self.stdout.write(f'\n📊 Company URLs Results:')
        self.stdout.write(f'   Valid URLs: {valid_urls}/{test_count}')
        self.stdout.write(f'   Invalid URLs: {invalid_urls}/{test_count}')
        self.stdout.write(f'   Success rate: {valid_urls/test_count*100:.1f}%')
    
    def test_linkedin_profiles(self):
        """Test LinkedIn profiles to ensure they're valid"""
        self.stdout.write(f'\n👥 Testing LinkedIn Profiles...')
        
        linkedin_profiles = DecisionMaker.objects.exclude(decision_maker_linkedin='')
        total_profiles = linkedin_profiles.count()
        
        if total_profiles == 0:
            self.stdout.write('❌ No LinkedIn profiles found.')
            return
        
        self.stdout.write(f'📋 Testing {total_profiles} LinkedIn profiles...')
        
        valid_profiles = 0
        invalid_profiles = 0
        test_count = min(15, total_profiles)  # Test first 15 profiles
        
        for i, profile in enumerate(linkedin_profiles[:test_count]):
            try:
                # Test the LinkedIn profile
                response = requests.head(profile.decision_maker_linkedin, timeout=10, allow_redirects=True)
                
                if response.status_code == 200:
                    valid_profiles += 1
                    self.stdout.write(f'✅ {profile.decision_maker_name}: {response.status_code}')
                else:
                    invalid_profiles += 1
                    self.stdout.write(f'❌ {profile.decision_maker_name}: {response.status_code}')
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                invalid_profiles += 1
                self.stdout.write(f'❌ {profile.decision_maker_name} - Error: {str(e)[:50]}...')
        
        self.stdout.write(f'\n📊 LinkedIn Profiles Results:')
        self.stdout.write(f'   Valid profiles: {valid_profiles}/{test_count}')
        self.stdout.write(f'   Invalid profiles: {invalid_profiles}/{test_count}')
        self.stdout.write(f'   Success rate: {valid_profiles/test_count*100:.1f}%')
    
    def create_test_data(self):
        """Create test data if none exists"""
        self.stdout.write('🔧 Creating test data...')
        
        # Run the comprehensive test to create data
        from django.core.management import call_command
        call_command('comprehensive_test', '--count', '10', '--market', 'USA', '--hours', '24')
