#!/usr/bin/env python
"""
Clear all job data from the database
"""

from django.core.management.base import BaseCommand
from dashboard.models import JobListing, Company, DecisionMaker

class Command(BaseCommand):
    help = 'Clear all job data from the database'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🗑️ Clearing all job data...')
        )
        
        # Count current data
        job_count = JobListing.objects.count()
        company_count = Company.objects.count()
        decision_maker_count = DecisionMaker.objects.count()
        
        self.stdout.write(f'📊 Current data:')
        self.stdout.write(f'   Jobs: {job_count}')
        self.stdout.write(f'   Companies: {company_count}')
        self.stdout.write(f'   Decision Makers: {decision_maker_count}')
        
        if job_count == 0:
            self.stdout.write(
                self.style.WARNING('⚠️ No data to delete.')
            )
            return
        
        # Delete all data
        DecisionMaker.objects.all().delete()
        JobListing.objects.all().delete()
        Company.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Successfully deleted:')
        )
        self.stdout.write(f'   {job_count} jobs')
        self.stdout.write(f'   {company_count} companies')
        self.stdout.write(f'   {decision_maker_count} decision makers')
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Database cleared! Ready for fresh scraping.')
        )
