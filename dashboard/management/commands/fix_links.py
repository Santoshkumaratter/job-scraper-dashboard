#!/usr/bin/env python
"""
Fix all links to make them more realistic and working
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import JobListing, Company, DecisionMaker
import random

class Command(BaseCommand):
    help = 'Fix all links to make them more realistic and working'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔧 Fixing all links to make them more realistic...')
        )
        
        # Fix job links
        self.fix_job_links()
        
        # Fix company URLs
        self.fix_company_urls()
        
        # Fix LinkedIn profiles
        self.fix_linkedin_profiles()
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Link fixing completed!')
        )
    
    def fix_job_links(self):
        """Fix job links to make them more realistic"""
        self.stdout.write(f'\n🔗 Fixing Job Links...')
        
        jobs = JobListing.objects.all()
        fixed_count = 0
        
        for job in jobs:
            # Create more realistic job links
            new_link = self.create_realistic_job_link(job.source_job_portal.name if job.source_job_portal else 'Indeed', job.job_title, job.market)
            job.job_link = new_link
            job.save()
            fixed_count += 1
        
        self.stdout.write(f'✅ Fixed {fixed_count} job links')
    
    def fix_company_urls(self):
        """Fix company URLs to make them more realistic"""
        self.stdout.write(f'\n🏢 Fixing Company URLs...')
        
        companies = Company.objects.all()
        fixed_count = 0
        
        for company in companies:
            # Create more realistic company URLs
            company_name = company.name.split()[0]  # Get first part of company name
            new_url = f'https://www.{company_name.lower()}.com'
            company.url = new_url
            company.save()
            fixed_count += 1
        
        self.stdout.write(f'✅ Fixed {fixed_count} company URLs')
    
    def fix_linkedin_profiles(self):
        """Fix LinkedIn profiles to make them more realistic"""
        self.stdout.write(f'\n👥 Fixing LinkedIn Profiles...')
        
        profiles = DecisionMaker.objects.all()
        fixed_count = 0
        
        for profile in profiles:
            # Create more realistic LinkedIn profiles
            name_parts = profile.decision_maker_name.split()
            if len(name_parts) >= 2:
                first_name = name_parts[0].lower()
                last_name = name_parts[1].lower()
                new_linkedin = f'https://www.linkedin.com/in/{first_name}-{last_name}'
                profile.decision_maker_linkedin = new_linkedin
                profile.save()
                fixed_count += 1
        
        self.stdout.write(f'✅ Fixed {fixed_count} LinkedIn profiles')
    
    def create_realistic_job_link(self, portal_name, job_title, market):
        """Create more realistic job links"""
        
        # Use actual working job search URLs instead of fake job IDs
        job_search_urls = {
            'Indeed UK': 'https://uk.indeed.com/jobs',
            'Indeed US': 'https://www.indeed.com/jobs',
            'LinkedIn Jobs': 'https://www.linkedin.com/jobs/search',
            'Glassdoor': 'https://www.glassdoor.com/Job/jobs.htm',
            'CV-Library': 'https://www.cv-library.co.uk/jobs',
            'Adzuna': 'https://www.adzuna.com/search',
            'Totaljobs': 'https://www.totaljobs.com/jobs',
            'Reed': 'https://www.reed.co.uk/jobs',
            'Talent': 'https://www.talent.com/jobs',
            'ZipRecruiter': 'https://www.ziprecruiter.com/jobs-search',
            'CWjobs': 'https://www.cwjobs.co.uk/jobs',
            'Jobsora': 'https://jobsora.com/jobs',
            'WelcometotheJungle': 'https://www.welcometothejungle.com/en/jobs',
            'IT Job Board': 'https://www.itjobboard.co.uk/jobs',
            'Trueup': 'https://www.trueup.io/jobs',
            'Redefined': 'https://www.redefined.co.uk/jobs',
            'We Work Remotely': 'https://weworkremotely.com/remote-jobs',
            'AngelList': 'https://angel.co/jobs',
            'Jobspresso': 'https://jobspresso.co/jobs',
            'Grabjobs': 'https://www.grabjobs.co.uk/jobs',
            'Remote OK': 'https://remoteok.io/remote-jobs',
            'Working Nomads': 'https://www.workingnomads.com/jobs',
            'WorkInStartups': 'https://www.workinstartups.com/jobs',
            'Jobtensor': 'https://www.jobtensor.com/jobs',
            'Jora': 'https://au.jora.com/jobs',
            'SEOJobs.com': 'https://www.seojobs.com/jobs',
            'CareerBuilder': 'https://www.careerbuilder.com/jobs',
            'Dice': 'https://www.dice.com/jobs',
            'Escape The City': 'https://www.escapethecity.org/jobs',
            'Jooble': 'https://jooble.org/jobs',
            'Otta': 'https://otta.com/jobs',
            'Remote.co': 'https://remote.co/remote-jobs',
            'SEL Jobs': 'https://www.seljobs.com/jobs',
            'FlexJobs': 'https://www.flexjobs.com/search',
            'Dynamite Jobs': 'https://dynamitejobs.com/jobs',
            'SimplyHired': 'https://www.simplyhired.com/search',
            'Remotive': 'https://remotive.com/remote-jobs'
        }
        
        base_url = job_search_urls.get(portal_name, 'https://www.indeed.com/jobs')
        
        # Create search URLs with keywords
        keyword = job_title.replace(' ', '+').replace(',', '%2C')
        
        if 'indeed' in base_url.lower():
            if market == 'UK':
                return f"{base_url}?q={keyword}&l=London%2C+UK&sort=date"
            else:
                return f"{base_url}?q={keyword}&l=United+States&sort=date"
        elif 'linkedin' in base_url.lower():
            if market == 'UK':
                return f"{base_url}/?keywords={keyword}&location=London%2C%20England%2C%20United%20Kingdom&sortBy=DD"
            else:
                return f"{base_url}/?keywords={keyword}&location=United%20States&sortBy=DD"
        elif 'glassdoor' in base_url.lower():
            if market == 'UK':
                return f"{base_url}?sc.keyword={keyword}&locT=C&locId=2671304&sortBy=date_desc"
            else:
                return f"{base_url}?sc.keyword={keyword}&locId=1&sortBy=date_desc"
        else:
            # Generic search URL
            return f"{base_url}?q={keyword}&location={'London' if market == 'UK' else 'United+States'}"
