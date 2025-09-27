from django.core.management.base import BaseCommand
from dashboard.google_sheets_integration import GoogleSheetsManager
from dashboard.models import JobListing

class Command(BaseCommand):
    help = 'Test Google Sheets integration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Testing Google Sheets Integration...'))
        
        # Get current job statistics
        total_jobs = JobListing.objects.count()
        technical_jobs = JobListing.objects.filter(is_technical=True).count()
        non_technical_jobs = JobListing.objects.filter(is_technical=False).count()
        
        self.stdout.write(f'📊 Current Database:')
        self.stdout.write(f'   Total Jobs: {total_jobs}')
        self.stdout.write(f'   Technical Jobs: {technical_jobs}')
        self.stdout.write(f'   Non-Technical Jobs: {non_technical_jobs}')
        
        # Test Google Sheets integration
        sheets_manager = GoogleSheetsManager()
        
        # Check if credentials exist
        import os
        creds_path = sheets_manager.credentials_path
        if os.path.exists(creds_path):
            self.stdout.write(self.style.SUCCESS(f'✅ Google Sheets credentials found at: {creds_path}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️ Google Sheets credentials NOT found at: {creds_path}'))
            self.stdout.write(self.style.WARNING('Please create google_sheets_credentials.json file'))
            return
        
        # Test authentication
        self.stdout.write('🔐 Testing Google Sheets authentication...')
        client = sheets_manager.get_google_sheet_client()
        if client:
            self.stdout.write(self.style.SUCCESS('✅ Google Sheets authentication successful!'))
        else:
            self.stdout.write(self.style.ERROR('❌ Google Sheets authentication failed!'))
            return
        
        # Test data formatting
        self.stdout.write('📋 Testing data formatting...')
        sample_jobs = JobListing.objects.all()[:5]
        formatted_data = sheets_manager.format_job_data_for_sheets(sample_jobs)
        
        self.stdout.write(f'✅ Formatted {len(formatted_data)} rows of sample data')
        if formatted_data:
            self.stdout.write('📝 Sample data row:')
            self.stdout.write(f'   {formatted_data[0]}')
        
        # Test saving to sheet (without actually saving)
        self.stdout.write('💾 Testing save functionality...')
        try:
            success, message = sheets_manager.save_all_jobs_to_sheet()
            if success:
                self.stdout.write(self.style.SUCCESS(f'✅ {message}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ {message}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
        
        self.stdout.write(self.style.SUCCESS('🎉 Google Sheets integration test completed!'))
