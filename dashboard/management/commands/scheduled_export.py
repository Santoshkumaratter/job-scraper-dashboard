from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, time, timedelta
import logging
import pytz

from dashboard.google_sheets_exporter import GoogleSheetsExporter

# Configure logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Export jobs to Google Sheets at scheduled times (11AM GST for UK, 4PM GST for USA)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force export regardless of time'
        )
        parser.add_argument(
            '--market',
            type=str,
            choices=['UK', 'USA', 'both'],
            default='both',
            help='Market to export (UK, USA, or both)'
        )
        parser.add_argument(
            '--is_technical',
            type=str,
            choices=['true', 'false', 'both'],
            default='both',
            help='Filter by technical job status'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting scheduled export...'))
        
        # Check if it's a weekend
        now = timezone.now()
        if now.weekday() >= 5:  # 5=Saturday, 6=Sunday
            self.stdout.write(self.style.WARNING('Today is a weekend. Exports only run on weekdays.'))
            return
        
        # Convert to Dubai time (GST/UTC+4)
        dubai_tz = pytz.timezone('Asia/Dubai')
        now_dubai = now.astimezone(dubai_tz)
        
        # Target times: 11:00 AM GST for UK, 4:00 PM GST for USA
        uk_export_time = time(hour=11, minute=0)
        usa_export_time = time(hour=16, minute=0)
        
        # Allow a window of +/- 15 minutes for the scheduled task
        time_window = 15  # minutes
        
        # Get technical filter
        if options['is_technical'] == 'true':
            is_technical = True
        elif options['is_technical'] == 'false':
            is_technical = False
        else:
            is_technical = None
        
        # Determine which exports to run
        run_uk = options['force'] or options['market'] in ['UK', 'both']
        run_usa = options['force'] or options['market'] in ['USA', 'both']
        
        # Check if current time is within UK export window
        uk_export_due = False
        if run_uk and not options['force']:
            start_time = datetime.combine(now_dubai.date(), uk_export_time) - timedelta(minutes=time_window)
            end_time = datetime.combine(now_dubai.date(), uk_export_time) + timedelta(minutes=time_window)
            
            uk_export_due = start_time <= now_dubai <= end_time
        
        # Check if current time is within USA export window
        usa_export_due = False
        if run_usa and not options['force']:
            start_time = datetime.combine(now_dubai.date(), usa_export_time) - timedelta(minutes=time_window)
            end_time = datetime.combine(now_dubai.date(), usa_export_time) + timedelta(minutes=time_window)
            
            usa_export_due = start_time <= now_dubai <= end_time
            
        # Initialize exporter
        exporter = GoogleSheetsExporter()
        
        # Run UK export if due or forced
        if options['force'] or uk_export_due:
            self.stdout.write(self.style.SUCCESS('Running UK export...'))
            try:
                success, message = exporter.export_uk_jobs(is_technical=is_technical)
                self.stdout.write(
                    self.style.SUCCESS(f'UK export: {message}') if success
                    else self.style.ERROR(f'UK export failed: {message}')
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'UK export error: {str(e)}'))
        
        # Run USA export if due or forced
        if options['force'] or usa_export_due:
            self.stdout.write(self.style.SUCCESS('Running USA export...'))
            try:
                success, message = exporter.export_usa_jobs(is_technical=is_technical)
                self.stdout.write(
                    self.style.SUCCESS(f'USA export: {message}') if success
                    else self.style.ERROR(f'USA export failed: {message}')
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'USA export error: {str(e)}'))
        
        # If no exports were due
        if not options['force'] and not uk_export_due and not usa_export_due:
            next_export = "UK export at 11:00 AM GST" if now_dubai.time() < uk_export_time else "USA export at 4:00 PM GST"
            if now_dubai.time() > usa_export_time:
                next_export = "UK export at 11:00 AM GST (tomorrow)"
                
            self.stdout.write(self.style.WARNING(
                f'No exports are due at this time. Next scheduled export: {next_export}'
            ))
            
        self.stdout.write(self.style.SUCCESS('Scheduled export completed!'))
