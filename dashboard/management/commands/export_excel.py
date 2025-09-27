#!/usr/bin/env python
"""
Management command to export job data to Excel in the exact format requested by client
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import JobListing, DecisionMaker
import csv
import os

class Command(BaseCommand):
    help = 'Export job data to Excel in the exact format requested by client'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path (default: job_listings_export.csv)',
            default='job_listings_export.csv'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of jobs to export (default: all)',
            default=None
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('📊 Starting Excel Export...')
        )
        
        # Get job listings with optimized queries
        queryset = JobListing.objects.select_related('company', 'source_job_portal').prefetch_related('company__decision_makers')
        
        # Apply limit if specified
        if options.get('limit'):
            queryset = queryset[:options['limit']]
        
        job_listings = list(queryset.order_by('-posted_date', '-scraped_at'))
        
        if not job_listings:
            self.stdout.write(
                self.style.WARNING('❌ No job listings found to export.')
            )
            return
        
        output_file = options.get('output', 'job_listings_export.csv')
        
        # Create CSV file with exact format as requested
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header with exact field names as per client requirements
            writer.writerow([
                'Field', 'Posted Date', 'Job Title', 'Company', 'Company URL', 'Company Size', 
                'Job Link', 'Job Portal', 'Location', 'First Name', 'Last Name', 'Title', 
                'LinkedIn', 'Email', 'Phone Number'
            ])
            
            # Pre-fetch all decision makers to avoid N+1 queries
            company_ids = [job.company.id for job in job_listings]
            decision_makers_dict = {}
            for dm in DecisionMaker.objects.filter(company_id__in=company_ids):
                if dm.company_id not in decision_makers_dict:
                    decision_makers_dict[dm.company_id] = []
                decision_makers_dict[dm.company_id].append(dm)
            
            # Write data rows
            for job in job_listings:
                # Get decision makers for this company (already fetched)
                decision_makers = decision_makers_dict.get(job.company.id, [])
                
                if decision_makers:
                    # Create a row for each decision maker
                    for dm in decision_makers:
                        # Split decision maker name into first and last name
                        name_parts = (dm.decision_maker_name or '').split(' ', 1)
                        first_name = name_parts[0] if name_parts else ''
                        last_name = name_parts[1] if len(name_parts) > 1 else ''
                        
                        writer.writerow([
                            'Technical' if job.is_technical else 'Non Technical',
                            job.posted_date.strftime('%m/%d/%Y') if job.posted_date else '',
                            job.job_title or '',
                            job.company.name or '',
                            job.company_url or '',
                            job.company_size or '',
                            job.job_link or '',
                            job.source_job_portal.name if job.source_job_portal else '',
                            job.location or '',
                            first_name,
                            last_name,
                            dm.decision_maker_title or '',
                            dm.decision_maker_linkedin or '',
                            dm.decision_maker_email or '',
                            dm.decision_maker_phone or ''
                        ])
                else:
                    # Add a row even if no decision makers
                    writer.writerow([
                        'Technical' if job.is_technical else 'Non Technical',
                        job.posted_date.strftime('%m/%d/%Y') if job.posted_date else '',
                        job.job_title or '',
                        job.company.name or '',
                        job.company_url or '',
                        job.company_size or '',
                        job.job_link or '',
                        job.source_job_portal.name if job.source_job_portal else '',
                        job.location or '',
                        '', '', '', '', '', ''  # Empty decision maker fields
                    ])
        
        # Get file info
        file_size = os.path.getsize(output_file)
        file_size_mb = file_size / (1024 * 1024)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Excel export completed successfully!')
        )
        self.stdout.write(f'📁 Output file: {output_file}')
        self.stdout.write(f'📊 Total jobs: {len(job_listings)}')
        self.stdout.write(f'📏 File size: {file_size_mb:.2f} MB')
        self.stdout.write(f'💾 Full path: {os.path.abspath(output_file)}')
        
        # Show sample of exported data
        self.stdout.write(
            self.style.SUCCESS('\n📋 SAMPLE EXPORTED DATA:')
        )
        
        with open(output_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            
            # Show header
            self.stdout.write(f'Header: {", ".join(rows[0])}')
            
            # Show first few data rows
            for i, row in enumerate(rows[1:6], 1):  # Show first 5 data rows
                self.stdout.write(f'Row {i}: {", ".join(row)}')
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Export completed! You can now open the CSV file in Excel.')
        )
