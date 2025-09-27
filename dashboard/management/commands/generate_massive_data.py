#!/usr/bin/env python
"""
Generate Massive Job Data for Testing
Creates 1000+ jobs from all 34+ portals to test the system
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from dashboard.google_sheets_integration import GoogleSheetsManager
from dashboard.comprehensive_scraper import ComprehensiveJobScraper
import time

class Command(BaseCommand):
    help = 'Generate massive job data (1000+ jobs) from all 34+ portals'

    def add_arguments(self, parser):
        parser.add_argument(
            '--target-jobs',
            type=int,
            default=1000,
            help='Target number of jobs to generate (default: 1000)'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing data before generating new data'
        )

    def handle(self, *args, **options):
        start_time = time.time()
        target_jobs = options['target_jobs']
        
        self.stdout.write(self.style.SUCCESS(f'🚀 Starting MASSIVE data generation for {target_jobs}+ jobs...'))
        
        if options['clear_existing']:
            self.stdout.write('🗑️ Clearing existing data...')
            from dashboard.models import JobListing, Company, DecisionMaker
            JobListing.objects.all().delete()
            Company.objects.all().delete()
            DecisionMaker.objects.all().delete()
            self.stdout.write('✅ Existing data cleared!')
        
        # Initialize Google Sheets manager
        sheets_manager = GoogleSheetsManager()
        
        # Generate massive data
        jobs_created = sheets_manager.generate_massive_test_data(target_jobs)
        
        # Get statistics
        stats = sheets_manager.get_job_statistics()
        
        elapsed = time.time() - start_time
        
        self.stdout.write(self.style.SUCCESS(f'✅ MASSIVE data generation completed in {elapsed:.1f} seconds!'))
        self.stdout.write(self.style.SUCCESS(f'📊 Created: {jobs_created} jobs'))
        self.stdout.write(self.style.SUCCESS(f'📈 Total jobs in database: {stats["total_jobs"]}'))
        self.stdout.write(self.style.SUCCESS(f'🔧 Technical jobs: {stats["technical_jobs"]}'))
        self.stdout.write(self.style.SUCCESS(f'📝 Non-technical jobs: {stats["non_technical_jobs"]}'))
        self.stdout.write(self.style.SUCCESS(f'🇺🇸 USA jobs: {stats["usa_jobs"]}'))
        self.stdout.write(self.style.SUCCESS(f'🇬🇧 UK jobs: {stats["uk_jobs"]}'))
        
        self.stdout.write('\n📊 Portal Statistics:')
        for portal, count in stats['portal_stats'].items():
            self.stdout.write(f'   {portal}: {count} jobs')
        
        # Test data formatting
        self.stdout.write('\n🧪 Testing data formatting...')
        job_listings = sheets_manager.get_all_job_data_for_sheets()
        formatted_rows = sheets_manager.format_job_data_for_sheets(job_listings[:5])  # Test first 5
        
        self.stdout.write('📋 Sample formatted data:')
        for i, row in enumerate(formatted_rows[:3]):  # Show first 3 rows
            self.stdout.write(f'   Row {i+1}: {row[0]} | {row[2]} | {row[3]} | {row[9]} {row[10]}')
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 System ready with {stats["total_jobs"]} jobs from all portals!'))
        self.stdout.write(self.style.SUCCESS('📄 Data can now be exported to Google Sheets format!'))
