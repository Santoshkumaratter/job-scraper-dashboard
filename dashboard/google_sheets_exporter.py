#!/usr/bin/env python
"""
Google Sheets Exporter for Job Data
Handles exporting job data to Google Sheets with specific formats
"""

import os
import csv
import logging
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Q
from .models import JobListing, Company, DecisionMaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional Google Sheets dependencies; fall back to CSV if unavailable
try:
    import gspread
from oauth2client.service_account import ServiceAccountCredentials
except Exception:  # ImportError or other issues
    gspread = None
    ServiceAccountCredentials = None

class GoogleSheetsExporter:
    """
    Handles exporting job data to Google Sheets with specific categorization
    and formatting requirements.
    """
    
    def __init__(self):
        # Allow overriding the sheet target via env
        self.sheet_id = os.environ.get("GOOGLE_SHEET_ID", "1PgnLi5C7zIBbu5XPNUT7EgVNPwfsC6RePaHEZ2qA-u0")
        self.credentials_path = os.path.join(
            os.path.dirname(__file__), 'google_sheets_credentials.json'
        )
        
    def get_google_sheet_client(self):
        """Authenticates and returns a gspread client"""
        try:
            # If libraries are unavailable, use fallback
            if gspread is None or ServiceAccountCredentials is None:
                logger.warning("gspread or oauth2client not available. Using CSV fallback.")
                return None
            
            if not os.path.exists(self.credentials_path):
                logger.error(f"Google Sheets credentials not found at: {self.credentials_path}")
                return None
                
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_path, scope
            )
            client = gspread.authorize(creds)
            return client
            
        except Exception as e:
            logger.error(f"Error authenticating with Google Sheets: {e}")
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
                worksheet = spreadsheet.add_worksheet(
                    title=sheet_name, rows=1000, cols=20
                )
            
            # Append the data
            if data:
                worksheet.append_rows(data)
                return True, f"Successfully appended {len(data)} rows to Google Sheet: {sheet_name}"
            else:
                return False, "No data to append"
                
        except Exception as e:
            logger.error(f"Error appending to Google Sheets: {e}")
            # Fallback: Save to CSV file instead
            return self.save_to_csv_fallback(data, sheet_name)
    
    def save_to_csv_fallback(self, data, sheet_name="Sheet1"):
        """Fallback method to save data as CSV when Google Sheets is not available"""
        try:            
            # Create exports directory if it doesn't exist
            exports_dir = os.path.join(settings.BASE_DIR, 'exports')
            os.makedirs(exports_dir, exist_ok=True)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{sheet_name.replace(' ', '_')}_{timestamp}.csv"
            filepath = os.path.join(exports_dir, filename)
            
            # Write CSV file
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                for row in data:
                    writer.writerow(row)
            
            return True, f"Data saved to CSV file: {filename}"
            
        except Exception as e:
            logger.error(f"Error saving to CSV fallback: {e}")
            return False, f"Error saving to CSV fallback: {e}"
            
    def get_job_data_for_export(self, category='all', filters=None):
        """
        Get job data for export based on category and filters
        
        Args:
            category: 'technical', 'non_technical', or 'all'
            filters: Dictionary of filters to apply
            
        Returns:
            Queryset of filtered job listings
        """
        # Start with all job listings with related data
        job_listings = JobListing.objects.select_related(
            'company', 'source_job_portal'
        ).prefetch_related(
            'company__decision_makers'
        )
        
        # Apply category filter
        if category == 'technical':
            job_listings = job_listings.filter(is_technical=True)
        elif category == 'non_technical':
            job_listings = job_listings.filter(is_technical=False)
            
        # Apply additional filters if provided
        if filters:
            if filters.get('market'):
                job_listings = job_listings.filter(market=filters['market'])
                
            if filters.get('job_type') and filters.get('job_type') != 'All':
                job_listings = job_listings.filter(job_type=filters['job_type'])
                
            if filters.get('keywords'):
                keyword_filter = Q()
                for keyword in filters['keywords']:
                    keyword_filter |= Q(job_title__icontains=keyword) | Q(description__icontains=keyword)
                job_listings = job_listings.filter(keyword_filter)
                
            if filters.get('job_boards'):
                job_listings = job_listings.filter(source_job_portal__name__in=filters['job_boards'])
                
            if filters.get('date_range'):
                date_range = filters['date_range']
                if date_range == '24hours':
                    job_listings = job_listings.filter(posted_date__gte=datetime.now().date() - timedelta(days=1))
                elif date_range == 'week':
                    job_listings = job_listings.filter(posted_date__gte=datetime.now().date() - timedelta(days=7))
                elif date_range == 'month':
                    job_listings = job_listings.filter(posted_date__gte=datetime.now().date() - timedelta(days=30))
        
        # Order by posting date (newest first)
        job_listings = job_listings.order_by('-posted_date')
        
        return job_listings
    
    def format_job_data_for_export(self, job_listings):
        """
        Format job data for export with all fields required by the client
        
        Args:
            job_listings: Queryset of job listings
            
        Returns:
            List of formatted rows
        """
        rows = []
        
        # Add header row
        header = [
            'Field', 'Posted Date', 'Job Title', 'Company', 'Company URL', 
            'Company Size', 'Market (USA/UK)', 'Source Job-Portal', 'Job Link', 
            'Location', 'All Decision_Maker_Name', 'Decision_Maker_Title', 
            'All Decision_Maker_LinkedIn', 'All Decision_Maker_Email', 'Decision_Maker_Phone'
        ]
        rows.append(header)
        
        for job in job_listings:
            decision_makers = job.company.decision_makers.all()
            
            if decision_makers:
                # Concatenate all decision makers for "All" columns
                names = []
                titles = []
                profiles = []
                emails = []
                phones = []
                
                for dm in decision_makers:
                    names.append(dm.decision_maker_name or '')
                    titles.append(dm.decision_maker_title or '')
                    profiles.append(dm.decision_maker_linkedin or '')
                    emails.append(dm.decision_maker_email or '')
                    phones.append(dm.decision_maker_phone or '')
                
                rows.append([
                    'Technical' if job.is_technical else 'Non-Technical',
                    job.posted_date.strftime('%m/%d/%Y') if job.posted_date else '',
                    job.job_title or '',
                    job.company.name or '',
                    job.company_url or '',
                    job.company_size or '',
                    job.market or '',
                    job.source_job_portal.name if job.source_job_portal else '',
                    job.job_link or '',
                    job.location or '',
                    '; '.join(names),
                    '; '.join(titles),
                    '; '.join(profiles),
                    '; '.join(emails),
                    '; '.join(phones),
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
                    job.market or '',
                    job.source_job_portal.name if job.source_job_portal else '',
                    job.job_link or '',
                    job.location or '',
                    '', '', '', '', ''  # Empty decision maker fields
                ])
        
        return rows
    
    def export_technical_jobs(self, filters=None):
        """Export technical jobs to Google Sheets"""
        try:
            # Get technical jobs
            job_listings = self.get_job_data_for_export(category='technical', filters=filters)
            
            # Format data
            rows = self.format_job_data_for_export(job_listings)
            
            if len(rows) > 1:  # Check if there are rows beyond the header
                # Append to sheet
                success, message = self.append_data_to_sheet(rows, "Technical Jobs")
                return success, message
            else:
                return False, "No technical jobs found"
                
        except Exception as e:
            logger.error(f"Error exporting technical jobs: {e}")
            return False, f"Error exporting technical jobs: {e}"
    
    def export_non_technical_jobs(self, filters=None):
        """Export non-technical jobs to Google Sheets"""
        try:
            # Get non-technical jobs
            job_listings = self.get_job_data_for_export(category='non_technical', filters=filters)
            
            # Format data
            rows = self.format_job_data_for_export(job_listings)
            
            if len(rows) > 1:  # Check if there are rows beyond the header
                # Append to sheet
                success, message = self.append_data_to_sheet(rows, "Non-Technical Jobs")
                return success, message
            else:
                return False, "No non-technical jobs found"
                
        except Exception as e:
            logger.error(f"Error exporting non-technical jobs: {e}")
            return False, f"Error exporting non-technical jobs: {e}"
    
    def export_all_jobs(self, filters=None):
        """Export all jobs to Google Sheets"""
        try:
            # Get all jobs
            job_listings = self.get_job_data_for_export(category='all', filters=filters)
            
            # Format data
            rows = self.format_job_data_for_export(job_listings)
            
            if len(rows) > 1:  # Check if there are rows beyond the header
                # Append to sheet
                success, message = self.append_data_to_sheet(rows, "All Jobs")
                return success, message
            else:
                return False, "No jobs found"
                
        except Exception as e:
            logger.error(f"Error exporting all jobs: {e}")
            return False, f"Error exporting all jobs: {e}"
    
    def export_uk_jobs(self, is_technical=None, filters=None):
        """Export UK jobs to Google Sheets"""
        try:
            # Override market filter
            if filters is None:
                filters = {}
            filters['market'] = 'UK'
            
            # Get jobs based on technical classification
            if is_technical is True:
                sheet_name = "UK Technical Jobs"
                job_listings = self.get_job_data_for_export(category='technical', filters=filters)
            elif is_technical is False:
                sheet_name = "UK Non-Technical Jobs"
                job_listings = self.get_job_data_for_export(category='non_technical', filters=filters)
            else:
                sheet_name = "UK Jobs"
                job_listings = self.get_job_data_for_export(category='all', filters=filters)
            
            # Format data
            rows = self.format_job_data_for_export(job_listings)
            
            if len(rows) > 1:  # Check if there are rows beyond the header
                # Append to sheet
                success, message = self.append_data_to_sheet(rows, sheet_name)
                return success, message
            else:
                return False, f"No {sheet_name.lower()} found"
                
        except Exception as e:
            logger.error(f"Error exporting UK jobs: {e}")
            return False, f"Error exporting UK jobs: {e}"
    
    def export_usa_jobs(self, is_technical=None, filters=None):
        """Export USA jobs to Google Sheets"""
        try:
            # Override market filter
            if filters is None:
                filters = {}
            filters['market'] = 'USA'
            
            # Get jobs based on technical classification
            if is_technical is True:
                sheet_name = "USA Technical Jobs"
                job_listings = self.get_job_data_for_export(category='technical', filters=filters)
            elif is_technical is False:
                sheet_name = "USA Non-Technical Jobs"
                job_listings = self.get_job_data_for_export(category='non_technical', filters=filters)
            else:
                sheet_name = "USA Jobs"
                job_listings = self.get_job_data_for_export(category='all', filters=filters)
            
            # Format data
            rows = self.format_job_data_for_export(job_listings)
            
            if len(rows) > 1:  # Check if there are rows beyond the header
                # Append to sheet
                success, message = self.append_data_to_sheet(rows, sheet_name)
                return success, message
            else:
                return False, f"No {sheet_name.lower()} found"
                
        except Exception as e:
            logger.error(f"Error exporting USA jobs: {e}")
            return False, f"Error exporting USA jobs: {e}"
    
    def create_csv_response(self, category='all', filters=None, filename=None):
        """Create CSV response for download"""
        try:
            # Get job listings based on category and filters
            job_listings = self.get_job_data_for_export(category, filters)
            
            # Format data
            rows = self.format_job_data_for_export(job_listings)
            
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                if category == 'technical':
                    filename = f"Technical_Jobs_{timestamp}.csv"
                elif category == 'non_technical':
                    filename = f"Non_Technical_Jobs_{timestamp}.csv"
                else:
                    filename = f"All_Jobs_{timestamp}.csv"
            
            # Create HTTP response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            writer = csv.writer(response)
            for row in rows:
                writer.writerow(row)
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating CSV response: {e}")
            
            # Return empty CSV on error
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="error_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            writer = csv.writer(response)
            writer.writerow(['Error', str(e)])
            return response