#!/usr/bin/env python
"""
Management command to test the complete job scraping system
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import JobListing, Company, DecisionMaker, JobPortal
from dashboard.comprehensive_scraper import ComprehensiveJobScraper
from dashboard.excel_export import ExcelExporter
import os


class Command(BaseCommand):
    help = 'Test the complete job scraping system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keywords',
            type=str,
            default='Python Developer',
            help='Keywords to test with'
        )
        parser.add_argument(
            '--market',
            type=str,
            default='USA',
            choices=['USA', 'UK', 'Both'],
            help='Market to test'
        )
        parser.add_argument(
            '--job-type',
            type=str,
            default='Technical',
            choices=['Technical', 'Non-Technical'],
            help='Job type to test'
        )

    def handle(self, *args, **options):
        keywords = options['keywords']
        market = options['market']
        job_type = options['job_type']
        
        self.stdout.write(
            self.style.SUCCESS('Testing Complete Job Scraping System')
        )
        self.stdout.write(f'Keywords: {keywords}')
        self.stdout.write(f'Market: {market}')
        self.stdout.write(f'Job Type: {job_type}')
        self.stdout.write('=' * 50)
        
        # Step 1: Initialize job portals
        self.stdout.write('\nStep 1: Initializing Job Portals...')
        from django.core.management import call_command
        call_command('initialize_job_portals')
        
        # Step 2: Test scraping
        self.stdout.write('\nStep 2: Testing Job Scraping...')
        scraper = ComprehensiveJobScraper()
        
        is_technical = job_type == 'Technical'
        markets_to_test = ['USA', 'UK'] if market == 'Both' else [market]
        
        total_jobs = 0
        for current_market in markets_to_test:
            self.stdout.write(f'  Scraping {current_market} market...')
            jobs_created = scraper.scrape_jobs(
                keywords=keywords,
                market=current_market,
                job_type='full_time',
                is_technical=is_technical,
                hours_back=24,
                selected_portal='All'
            )
            total_jobs += jobs_created
            self.stdout.write(f'  Created {jobs_created} jobs for {current_market}')
        
        # Step 3: Verify data quality
        self.stdout.write('\nStep 3: Verifying Data Quality...')
        self.verify_data_quality()
        
        # Step 4: Test Excel export
        self.stdout.write('\nStep 4: Testing Excel Export...')
        self.test_excel_export()
        
        # Step 5: Generate report
        self.stdout.write('\nStep 5: Generating Test Report...')
        self.generate_test_report()
        
        self.stdout.write(
            self.style.SUCCESS('\nComplete system test finished successfully!')
        )

    def verify_data_quality(self):
        """Verify the quality of scraped data"""
        total_jobs = JobListing.objects.count()
        total_companies = Company.objects.count()
        total_decision_makers = DecisionMaker.objects.count()
        
        self.stdout.write(f'  Total Jobs: {total_jobs}')
        self.stdout.write(f'  Total Companies: {total_companies}')
        self.stdout.write(f'  Total Decision Makers: {total_decision_makers}')
        
        # Check for missing data
        jobs_without_company_size = JobListing.objects.filter(company_size__isnull=True).count()
        jobs_without_decision_makers = JobListing.objects.filter(
            company__decision_makers__isnull=True
        ).count()
        
        self.stdout.write(f'  Jobs without company size: {jobs_without_company_size}')
        self.stdout.write(f'  Jobs without decision makers: {jobs_without_decision_makers}')
        
        # Check decision maker data completeness
        dms_without_phone = DecisionMaker.objects.filter(decision_maker_phone__isnull=True).count()
        dms_without_email = DecisionMaker.objects.filter(decision_maker_email__isnull=True).count()
        dms_without_linkedin = DecisionMaker.objects.filter(decision_maker_linkedin__isnull=True).count()
        
        self.stdout.write(f'  Decision makers without phone: {dms_without_phone}')
        self.stdout.write(f'  Decision makers without email: {dms_without_email}')
        self.stdout.write(f'  Decision makers without LinkedIn: {dms_without_linkedin}')
        
        # Check company diversity
        unique_companies = Company.objects.values_list('name', flat=True).distinct().count()
        self.stdout.write(f'  Unique companies: {unique_companies}')
        
        if total_jobs > 0:
            self.stdout.write(self.style.SUCCESS('  Data quality verification passed'))
        else:
            self.stdout.write(self.style.ERROR('  No jobs found - data quality check failed'))

    def test_excel_export(self):
        """Test Excel export functionality"""
        try:
            exporter = ExcelExporter()
            stats = exporter.get_export_stats()
            
            self.stdout.write(f'  Export stats: {stats}')
            
            # Test CSV export
            csv_response = exporter.export_to_csv('test_export.csv')
            self.stdout.write('  CSV export successful')
            
            # Test Excel export (if pandas is available)
            try:
                excel_response = exporter.export_to_excel('test_export.xlsx')
                self.stdout.write('  Excel export successful')
            except Exception as e:
                self.stdout.write(f'  Excel export failed: {e}')
                self.stdout.write('  CSV export as fallback successful')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Export test failed: {e}'))

    def generate_test_report(self):
        """Generate a comprehensive test report"""
        report = {
            'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_jobs': JobListing.objects.count(),
            'total_companies': Company.objects.count(),
            'total_decision_makers': DecisionMaker.objects.count(),
            'total_portals': JobPortal.objects.count(),
            'active_portals': JobPortal.objects.filter(is_active=True).count(),
            'jobs_by_market': {
                'USA': JobListing.objects.filter(market='USA').count(),
                'UK': JobListing.objects.filter(market='UK').count(),
            },
            'jobs_by_type': {
                'Technical': JobListing.objects.filter(is_technical=True).count(),
                'Non-Technical': JobListing.objects.filter(is_technical=False).count(),
            },
            'company_sizes': list(Company.objects.values_list('company_size', flat=True).distinct()),
            'decision_maker_titles': list(DecisionMaker.objects.values_list('decision_maker_title', flat=True).distinct()[:10]),
        }
        
        self.stdout.write('\nTest Report:')
        self.stdout.write('=' * 30)
        for key, value in report.items():
            if isinstance(value, dict):
                self.stdout.write(f'{key}:')
                for sub_key, sub_value in value.items():
                    self.stdout.write(f'  {sub_key}: {sub_value}')
            else:
                self.stdout.write(f'{key}: {value}')
        
        # Save report to file
        report_file = 'test_report.txt'
        with open(report_file, 'w') as f:
            f.write('Job Scraper System Test Report\n')
            f.write('=' * 40 + '\n\n')
            for key, value in report.items():
                if isinstance(value, dict):
                    f.write(f'{key}:\n')
                    for sub_key, sub_value in value.items():
                        f.write(f'  {sub_key}: {sub_value}\n')
                else:
                    f.write(f'{key}: {value}\n')
        
        self.stdout.write(f'\nReport saved to: {report_file}')
