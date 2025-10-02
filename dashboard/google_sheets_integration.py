#!/usr/bin/env python
"""
Google Sheets Integration for Job Data
Handles appending new job data to existing Google Sheets
"""

import csv
import io
import os
import json
from django.http import HttpResponse
from django.db.models import Q
from django.conf import settings
from .models import JobListing
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class GoogleSheetsManager:
    """Manages Google Sheets integration and data appending"""
    
    def __init__(self):
        self.sheet_id = "1KwJ3mFWeit6K10IuXQHXiYPJUUqkTE7tSPl9pTaMhwY"  # Your Google Sheet ID
        self.credentials_path = os.path.join(os.path.dirname(__file__), 'google_sheets_credentials.json')
    
    def get_google_sheet_client(self):
        """Authenticates and returns a gspread client"""
        try:
            if not os.path.exists(self.credentials_path):
                print(f"❌ Google Sheets credentials not found at: {self.credentials_path}")
                print("💡 Creating fallback solution - data will be exported as CSV instead")
                return None
                
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_path, scope)
            client = gspread.authorize(creds)
            return client
        except Exception as e:
            print(f"❌ Error authenticating with Google Sheets: {e}")
            print("💡 Using fallback solution - data will be exported as CSV instead")
            return None
    
    def append_data_to_sheet(self, data, sheet_name="Sheet1"):
        """Appends data to the specified Google Sheet or creates CSV fallback"""
        try:
            client = self.get_google_sheet_client()
            if not client:
                # Fallback: Save to CSV file instead
                return self.save_to_csv_fallback(data, sheet_name)
            
            # Open the spreadsheet
            spreadsheet = client.open_by_key(self.sheet_id)
            
            # Get or create the worksheet
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            
            # Append the data
            if data:
                worksheet.append_rows(data)
                return True, f"Successfully appended {len(data)} rows to Google Sheet: {sheet_name}"
            else:
                return False, "No data to append"
                
        except Exception as e:
            # Fallback: Save to CSV file instead
            return self.save_to_csv_fallback(data, sheet_name)
    
    def save_to_csv_fallback(self, data, sheet_name="Sheet1"):
        """Fallback method to save data as CSV when Google Sheets is not available"""
        try:
            import csv
            from django.conf import settings
            import os
            
            # Create exports directory if it doesn't exist
            exports_dir = os.path.join(settings.BASE_DIR, 'exports')
            os.makedirs(exports_dir, exist_ok=True)
            
            # Create filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{sheet_name.replace(' ', '_')}_{timestamp}.csv"
            filepath = os.path.join(exports_dir, filename)
            
            # Write CSV file
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                for row in data:
                    writer.writerow(row)
            
            return True, f"✅ Data saved to CSV file: {filename} (Google Sheets not configured)"
            
        except Exception as e:
            return False, f"Error saving to CSV fallback: {e}"
    
    def save_technical_jobs_to_sheet(self):
        """Save technical jobs to Google Sheet"""
        try:
            # Get technical jobs
            technical_jobs = JobListing.objects.filter(is_technical=True).select_related(
                'company', 'source_job_portal'
            ).prefetch_related('company__decision_makers')
            
            # Format data
            rows = self.format_job_data_for_sheets(technical_jobs)
            
            if rows:
                # Add header row
                header = [
                    'Field', 'Posted Date', 'Job Title', 'Company', 'Company URL', 'Company Size',
                    'Job Link', 'Job Portal', 'Location', 'First Name', 'Last Name', 'Title',
                    'LinkedIn', 'Email', 'Phone Number'
                ]
                rows.insert(0, header)
                
                # Append to sheet
                success, message = self.append_data_to_sheet(rows, "Technical Jobs")
                return success, message
            else:
                return False, "No technical jobs found"
                
        except Exception as e:
            return False, f"Error saving technical jobs: {e}"
    
    def save_non_technical_jobs_to_sheet(self):
        """Save non-technical jobs to Google Sheet"""
        try:
            # Get non-technical jobs
            non_technical_jobs = JobListing.objects.filter(is_technical=False).select_related(
                'company', 'source_job_portal'
            ).prefetch_related('company__decision_makers')
            
            # Format data
            rows = self.format_job_data_for_sheets(non_technical_jobs)
            
            if rows:
                # Add header row
                header = [
                    'Field', 'Posted Date', 'Job Title', 'Company', 'Company URL', 'Company Size',
                    'Job Link', 'Job Portal', 'Location', 'First Name', 'Last Name', 'Title',
                    'LinkedIn', 'Email', 'Phone Number'
                ]
                rows.insert(0, header)
                
                # Append to sheet
                success, message = self.append_data_to_sheet(rows, "Non-Technical Jobs")
                return success, message
            else:
                return False, "No non-technical jobs found"
                
        except Exception as e:
            return False, f"Error saving non-technical jobs: {e}"
    
    def save_all_jobs_to_sheet(self):
        """Save all jobs to Google Sheet in the exact format from the sample"""
        try:
            # Get all jobs
            all_jobs = JobListing.objects.all().select_related(
                'company', 'source_job_portal'
            ).prefetch_related('company__decision_makers')
            
            # Format data
            rows = self.format_job_data_for_sheets(all_jobs)
            
            if rows:
                # Add header row
                header = [
                    'Field', 'Posted Date', 'Job Title', 'Company', 'Company URL', 'Company Size',
                    'Job Link', 'Job Portal', 'Location', 'First Name', 'Last Name', 'Title',
                    'LinkedIn', 'Email', 'Phone Number'
                ]
                rows.insert(0, header)
                
                # Append to sheet
                success, message = self.append_data_to_sheet(rows, "All Jobs")
                return success, message
            else:
                return False, "No jobs found"
                
        except Exception as e:
            return False, f"Error saving all jobs: {e}"
        
    def get_all_job_data_for_sheets(self, filters=None):
        """Get all job data formatted for Google Sheets"""
        
        # Get all job listings with related data
        job_listings = JobListing.objects.select_related(
            'company', 'source_job_portal'
        ).prefetch_related(
            'company__decision_makers'
        ).all()
        
        # Apply filters if provided
        if filters:
            if filters.get('market'):
                job_listings = job_listings.filter(market=filters['market'])
            if filters.get('is_technical') is not None:
                job_listings = job_listings.filter(is_technical=filters['is_technical'])
            if filters.get('keywords'):
                keyword_filter = Q()
                for keyword in filters['keywords']:
                    keyword_filter |= Q(job_title__icontains=keyword) | Q(description__icontains=keyword)
                job_listings = job_listings.filter(keyword_filter)
        
        return job_listings
    
    def format_job_data_for_sheets(self, job_listings):
        """Format job data exactly like the Google Sheet sample"""
        
        rows = []
        
        for job in job_listings:
            decision_makers = job.company.decision_makers.all()
            
            if decision_makers:
                # Create a row for each decision maker
                for dm in decision_makers:
                    # Split decision maker name into first and last name
                    name_parts = (dm.decision_maker_name or '').split(' ', 1)
                    first_name = name_parts[0] if name_parts else ''
                    last_name = name_parts[1] if len(name_parts) > 1 else ''
                    
                    rows.append([
                        'Technical' if job.is_technical else 'Non-Technical',
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
                rows.append([
                    'Technical' if job.is_technical else 'Non-Technical',
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
        
        return rows
    
    def create_csv_response(self, rows, filename="job_data.csv"):
        """Create CSV response for download or Google Sheets upload"""
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow([
            'Field', 'Posted Date', 'Job Title', 'Company', 'Company URL', 'Company Size',
            'Job Link', 'Job Portal', 'Location', 'First Name', 'Last Name', 'Title',
            'LinkedIn', 'Email', 'Phone Number'
        ])
        
        # Write data rows
        for row in rows:
            writer.writerow(row)
        
        return response
    
    def get_job_statistics(self):
        """Get statistics about current job data"""
        
        total_jobs = JobListing.objects.count()
        technical_jobs = JobListing.objects.filter(is_technical=True).count()
        non_technical_jobs = JobListing.objects.filter(is_technical=False).count()
        
        # Count by market
        usa_jobs = JobListing.objects.filter(market='USA').count()
        uk_jobs = JobListing.objects.filter(market='UK').count()
        
        # Count by portal
        portal_stats = {}
        for job in JobListing.objects.select_related('source_job_portal').all():
            portal_name = job.source_job_portal.name if job.source_job_portal else 'Unknown'
            portal_stats[portal_name] = portal_stats.get(portal_name, 0) + 1
        
        return {
            'total_jobs': total_jobs,
            'technical_jobs': technical_jobs,
            'non_technical_jobs': non_technical_jobs,
            'usa_jobs': usa_jobs,
            'uk_jobs': uk_jobs,
            'portal_stats': portal_stats
        }
    
    def generate_massive_test_data(self, target_jobs=1000):
        """Generate massive test data to reach target volume"""
        
        from .comprehensive_scraper import ComprehensiveJobScraper
        
        # Technical keywords from your list
        technical_keywords = [
            'React Native Developer', 'Full Stack Developer', 'Python Developer',
            'Django Developer', 'FastAPI Engineer', 'Cloud Engineer', 'DevOps Engineer',
            'AI Engineer', 'Machine Learning Engineer', 'LLM Engineer', 'Applied Scientist',
            'Software Engineer', 'Backend Engineer', 'Frontend Developer', 'Mobile Engineer'
        ]
        
        # Non-technical keywords from your list  
        non_technical_keywords = [
            'SEO Specialist', 'Digital Marketing Manager', 'Marketing Specialist',
            'Content Marketing Specialist', 'Paid Advertising Manager', 'Media Buyer',
            'Google Ads Expert', 'PPC Specialist', 'Paid Search Manager', 'Growth Marketing Manager'
        ]
        
        scraper = ComprehensiveJobScraper()
        jobs_created = 0
        
        # Generate technical jobs for USA
        print(f"🚀 Generating technical jobs for USA...")
        result = scraper.scrape_jobs(
            keywords=technical_keywords[:8],
            market='USA',
            job_type='full_time',
            is_technical=True,
            hours_back=168  # 7 days
        )
        jobs_created += result
        
        # Generate non-technical jobs for USA
        print(f"🚀 Generating non-technical jobs for USA...")
        result = scraper.scrape_jobs(
            keywords=non_technical_keywords[:8],
            market='USA',
            job_type='full_time',
            is_technical=False,
            hours_back=168  # 7 days
        )
        jobs_created += result
        
        # Generate technical jobs for UK
        print(f"🚀 Generating technical jobs for UK...")
        result = scraper.scrape_jobs(
            keywords=technical_keywords[8:],
            market='UK',
            job_type='full_time',
            is_technical=True,
            hours_back=168  # 7 days
        )
        jobs_created += result
        
        # Generate non-technical jobs for UK
        print(f"🚀 Generating non-technical jobs for UK...")
        result = scraper.scrape_jobs(
            keywords=non_technical_keywords[8:],
            market='UK',
            job_type='full_time',
            is_technical=False,
            hours_back=168  # 7 days
        )
        jobs_created += result
        
        print(f"✅ Generated {jobs_created} total jobs!")
        return jobs_created
