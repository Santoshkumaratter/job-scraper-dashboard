"""
Django management command to export jobs to Google Sheets
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime

from dashboard.google_sheets_exporter import GoogleSheetsExporter


class Command(BaseCommand):
    """
    Export jobs to Google Sheets
    """
    
    help = 'Export jobs to Google Sheets with various filtering options'
    
    def add_arguments(self, parser):
        """Add command-line arguments"""
        parser.add_argument(
            '--market',
            type=str,
            choices=['USA', 'UK', 'All'],
            default='All',
            help='Market to filter jobs by (USA or UK)'
        )
        
        parser.add_argument(
            '--is_technical',
            type=str,
            choices=['true', 'false', 'all'],
            default='all',
            help='Export technical or non-technical jobs'
        )
        
        parser.add_argument(
            '--days_back',
            type=int,
            default=1,
            help='Number of days to look back for jobs'
        )
        
        parser.add_argument(
            '--title_prefix',
            type=str,
            default='Job Scraper Data',
            help='Prefix for spreadsheet title'
        )
        
        parser.add_argument(
            '--email',
            type=str,
            default='',
            help='Email address to share the spreadsheet with'
        )
        
        parser.add_argument(
            '--uk_time',
            action='store_true',
            help='Export UK jobs (run at 11:00 AM GST)'
        )
        
        parser.add_argument(
            '--usa_time',
            action='store_true',
            help='Export USA jobs (run at 4:00 PM GST)'
        )
    
    def handle(self, *args, **options):
        """Handle the command"""
        # Parse options
        market = options['market']
        is_technical_str = options['is_technical']
        days_back = options['days_back']
        title_prefix = options['title_prefix']
        email = options['email'] if options['email'] else None
        uk_time = options['uk_time']
        usa_time = options['usa_time']
        
        # Convert is_technical to boolean or None
        is_technical = None
        if is_technical_str == 'true':
            is_technical = True
        elif is_technical_str == 'false':
            is_technical = False
        
        # Initialize exporter
        exporter = GoogleSheetsExporter()
        
        # Handle specific schedule exports
        if uk_time:
            self.stdout.write(self.style.SUCCESS('Exporting UK jobs at scheduled time...'))
            
            # UK Technical jobs
            uk_tech_title = f"UK Technical Jobs ({datetime.now().strftime('%Y-%m-%d')})"
            uk_tech_success = exporter.export_jobs_by_portal(uk_tech_title, "UK", True, days_back, email)
            
            if uk_tech_success:
                self.stdout.write(self.style.SUCCESS(f'Successfully exported UK Technical jobs to {uk_tech_title}'))
            else:
                self.stdout.write(self.style.ERROR(f'Failed to export UK Technical jobs'))
            
            # UK Non-Technical jobs
            uk_nontech_title = f"UK Non-Technical Jobs ({datetime.now().strftime('%Y-%m-%d')})"
            uk_nontech_success = exporter.export_jobs_by_portal(uk_nontech_title, "UK", False, days_back, email)
            
            if uk_nontech_success:
                self.stdout.write(self.style.SUCCESS(f'Successfully exported UK Non-Technical jobs to {uk_nontech_title}'))
            else:
                self.stdout.write(self.style.ERROR(f'Failed to export UK Non-Technical jobs'))
                
            return
            
        elif usa_time:
            self.stdout.write(self.style.SUCCESS('Exporting USA jobs at scheduled time...'))
            
            # USA Technical jobs
            usa_tech_title = f"USA Technical Jobs ({datetime.now().strftime('%Y-%m-%d')})"
            usa_tech_success = exporter.export_jobs_by_portal(usa_tech_title, "USA", True, days_back, email)
            
            if usa_tech_success:
                self.stdout.write(self.style.SUCCESS(f'Successfully exported USA Technical jobs to {usa_tech_title}'))
            else:
                self.stdout.write(self.style.ERROR(f'Failed to export USA Technical jobs'))
            
            # USA Non-Technical jobs
            usa_nontech_title = f"USA Non-Technical Jobs ({datetime.now().strftime('%Y-%m-%d')})"
            usa_nontech_success = exporter.export_jobs_by_portal(usa_nontech_title, "USA", False, days_back, email)
            
            if usa_nontech_success:
                self.stdout.write(self.style.SUCCESS(f'Successfully exported USA Non-Technical jobs to {usa_nontech_title}'))
            else:
                self.stdout.write(self.style.ERROR(f'Failed to export USA Non-Technical jobs'))
                
            return
        
        # Handle regular exports
        if market == 'All' and is_technical is None:
            # Export all jobs to separate spreadsheets
            self.stdout.write(self.style.SUCCESS('Exporting all jobs...'))
            
            results = exporter.export_all_jobs(title_prefix, days_back, email)
            
            if all(results):
                self.stdout.write(self.style.SUCCESS('Successfully exported all jobs'))
            else:
                self.stdout.write(self.style.ERROR('Failed to export some jobs'))
                
        else:
            # Export specific jobs
            if market == 'All':
                # Export both USA and UK for the specified job type
                markets = ['USA', 'UK']
            else:
                markets = [market]
                
            if is_technical is None:
                # Export both technical and non-technical jobs for the specified market
                is_technical_values = [True, False]
            else:
                is_technical_values = [is_technical]
                
            # Export each combination
            for m in markets:
                for t in is_technical_values:
                    job_type = "Technical" if t else "Non-Technical"
                    title = f"{title_prefix} - {m} {job_type} ({datetime.now().strftime('%Y-%m-%d')})"
                    
                    self.stdout.write(self.style.SUCCESS(f'Exporting {m} {job_type} jobs...'))
                    
                    success = exporter.export_jobs_by_portal(title, m, t, days_back, email)
                    
                    if success:
                        self.stdout.write(self.style.SUCCESS(f'Successfully exported {m} {job_type} jobs to {title}'))
                    else:
                        self.stdout.write(self.style.ERROR(f'Failed to export {m} {job_type} jobs'))
