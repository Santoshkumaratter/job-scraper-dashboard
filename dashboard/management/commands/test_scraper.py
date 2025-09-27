#!/usr/bin/env python
"""
Management command to test the job scraper with provided keywords
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.comprehensive_scraper import ComprehensiveJobScraper
from dashboard.models import JobListing, Company, DecisionMaker

class Command(BaseCommand):
    help = 'Test the job scraper with technical and non-technical keywords'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keywords',
            type=str,
            help='Keywords to search for (comma-separated)',
            default=''
        )
        parser.add_argument(
            '--market',
            type=str,
            choices=['USA', 'UK'],
            default='USA',
            help='Market to search (USA or UK)'
        )
        parser.add_argument(
            '--technical',
            action='store_true',
            help='Search for technical jobs'
        )
        parser.add_argument(
            '--non-technical',
            action='store_true',
            help='Search for non-technical jobs'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting Job Scraper Test...')
        )
        
        # Default keywords from client requirements
        technical_keywords = [
            'React Native Developer', 'Senior React Native Developer', 'Full Stack Developer',
            'Senior Full Stack Developer', 'Python Developer', 'Django Developer',
            'FastAPI Engineer', 'Cloud Engineer', 'DevOps Engineer', 'AI Engineer',
            'Machine Learning Engineer', 'LLM Engineer', 'Generative AI Engineer'
        ]
        
        non_technical_keywords = [
            'SEO Specialist', 'SEO Manager', 'Digital Marketing Specialist',
            'Digital Marketing Manager', 'Marketing Manager', 'Content Marketing Specialist',
            'Paid Advertising Manager', 'PPC Specialist', 'Google Ads Expert'
        ]
        
        keywords = options.get('keywords', '')
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(',')]
        else:
            # Use default keywords based on type
            if options.get('technical'):
                keyword_list = technical_keywords
            elif options.get('non_technical'):
                keyword_list = non_technical_keywords
            else:
                # Test both types
                keyword_list = technical_keywords + non_technical_keywords
        
        market = options.get('market', 'USA')
        
        # Test technical jobs
        if not options.get('non_technical'):
            self.stdout.write(
                self.style.WARNING('🔧 Testing Technical Jobs...')
            )
            
            scraper = ComprehensiveJobScraper()
            technical_jobs = scraper.scrape_jobs(
                keywords=keyword_list[:5] if len(keyword_list) > 5 else keyword_list,
                market=market,
                job_type='full_time',
                is_technical=True,
                hours_back=24
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Technical Jobs Created: {technical_jobs}')
            )
        
        # Test non-technical jobs
        if not options.get('technical'):
            self.stdout.write(
                self.style.WARNING('📊 Testing Non-Technical Jobs...')
            )
            
            scraper = ComprehensiveJobScraper()
            non_technical_jobs = scraper.scrape_jobs(
                keywords=keyword_list[-5:] if len(keyword_list) > 5 else keyword_list,
                market=market,
                job_type='full_time',
                is_technical=False,
                hours_back=24
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Non-Technical Jobs Created: {non_technical_jobs}')
            )
        
        # Display summary
        total_jobs = JobListing.objects.count()
        total_companies = Company.objects.count()
        total_decision_makers = DecisionMaker.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS('\n📊 SCRAPING SUMMARY:')
        )
        self.stdout.write(f'Total Jobs: {total_jobs}')
        self.stdout.write(f'Total Companies: {total_companies}')
        self.stdout.write(f'Total Decision Makers: {total_decision_makers}')
        
        # Show sample data
        self.stdout.write(
            self.style.SUCCESS('\n📋 SAMPLE JOB DATA:')
        )
        
        sample_jobs = JobListing.objects.select_related('company', 'source_job_portal').prefetch_related('company__decision_makers')[:5]
        
        for job in sample_jobs:
            self.stdout.write(f'\nJob: {job.job_title}')
            self.stdout.write(f'Company: {job.company.name}')
            self.stdout.write(f'Portal: {job.source_job_portal.name if job.source_job_portal else "N/A"}')
            self.stdout.write(f'Location: {job.location}')
            self.stdout.write(f'Posted: {job.posted_date}')
            self.stdout.write(f'Technical: {"Yes" if job.is_technical else "No"}')
            
            # Show decision makers
            decision_makers = job.company.decision_makers.all()
            if decision_makers:
                self.stdout.write('Decision Makers:')
                for dm in decision_makers:
                    self.stdout.write(f'  - {dm.decision_maker_name} ({dm.decision_maker_title})')
                    self.stdout.write(f'    Email: {dm.decision_maker_email}')
                    self.stdout.write(f'    Phone: {dm.decision_maker_phone}')
                    self.stdout.write(f'    LinkedIn: {dm.decision_maker_linkedin}')
            else:
                self.stdout.write('Decision Makers: None')
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Scraper test completed successfully!')
        )
        self.stdout.write(
            self.style.SUCCESS('💡 You can now export the data to Excel using the dashboard.')
        )
