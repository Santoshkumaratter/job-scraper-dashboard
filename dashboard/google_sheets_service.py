"""
Google Sheets integration service for job scraper
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from django.conf import settings
from django.utils import timezone

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

from .models import JobListing, Company, DecisionMaker


class GoogleSheetsService:
    """Service for interacting with Google Sheets API"""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    CREDENTIALS_FILE = 'credentials.json'
    TOKEN_FILE = 'token.json'
    
    def __init__(self):
        self.service = None
        self.credentials = None
        
    def authenticate(self):
        """Authenticate with Google Sheets API"""
        if not GOOGLE_SHEETS_AVAILABLE:
            raise ImportError("Google Sheets API libraries not installed")
            
        creds = None
        # The file token.json stores the user's access and refresh tokens.
        if os.path.exists(self.TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(self.TOKEN_FILE, self.SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.CREDENTIALS_FILE):
                    raise FileNotFoundError(f"Credentials file {self.CREDENTIALS_FILE} not found")
                    
                flow = Flow.from_client_secrets_file(self.CREDENTIALS_FILE, self.SCOPES)
                flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                
                auth_url, _ = flow.authorization_url(prompt='consent')
                print(f'Please go to this URL and authorize the application: {auth_url}')
                auth_code = input('Enter the authorization code: ')
                flow.fetch_token(code=auth_code)
                creds = flow.credentials
            
            # Save the credentials for the next run
            with open(self.TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        
        self.credentials = creds
        self.service = build('sheets', 'v4', credentials=creds)
        return True
    
    def create_spreadsheet(self, title: str) -> str:
        """Create a new spreadsheet and return its ID"""
        if not self.service:
            self.authenticate()
            
        spreadsheet_body = {
            'properties': {
                'title': title
            }
        }
        
        spreadsheet = self.service.spreadsheets().create(
            body=spreadsheet_body,
            fields='spreadsheetId'
        ).execute()
        
        return spreadsheet.get('spreadsheetId')
    
    def get_spreadsheet_url(self, spreadsheet_id: str) -> str:
        """Get the URL for a spreadsheet"""
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
    
    def create_technical_sheet(self, spreadsheet_id: str, sheet_name: str = "Technical Jobs"):
        """Create a sheet for technical jobs with proper headers"""
        if not self.service:
            self.authenticate()
            
        # Create the sheet
        request_body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': sheet_name
                    }
                }
            }]
        }
        
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=request_body
        ).execute()
        
        # Add headers
        headers = [
            'Field', 'Posted Date', 'Job Title', 'Company', 'Company URL', 
            'Company Size', 'Job Link', 'Job Portal', 'Location', 
            'First Name', 'Last Name', 'Title', 'LinkedIn', 'Email', 'Phone Number'
        ]
        
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1:O1",
            valueInputOption='RAW',
            body={'values': [headers]}
        ).execute()
        
        # Format headers
        self._format_headers(spreadsheet_id, sheet_name)
    
    def create_non_technical_sheet(self, spreadsheet_id: str, sheet_name: str = "Non-Technical Jobs"):
        """Create a sheet for non-technical jobs with proper headers"""
        self.create_technical_sheet(spreadsheet_id, sheet_name)
    
    def _format_headers(self, spreadsheet_id: str, sheet_name: str):
        """Format the header row"""
        if not self.service:
            self.authenticate()
            
        requests = [{
            'repeatCell': {
                'range': {
                    'sheetId': self._get_sheet_id(spreadsheet_id, sheet_name),
                    'startRowIndex': 0,
                    'endRowIndex': 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {
                            'red': 0.2,
                            'green': 0.4,
                            'blue': 0.8
                        },
                        'textFormat': {
                            'foregroundColor': {
                                'red': 1.0,
                                'green': 1.0,
                                'blue': 1.0
                            },
                            'fontSize': 12,
                            'bold': True
                        }
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat)'
            }
        }]
        
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()
    
    def _get_sheet_id(self, spreadsheet_id: str, sheet_name: str) -> int:
        """Get the sheet ID for a given sheet name"""
        if not self.service:
            self.authenticate()
            
        spreadsheet = self.service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        
        for sheet in spreadsheet['sheets']:
            if sheet['properties']['title'] == sheet_name:
                return sheet['properties']['sheetId']
        
        raise ValueError(f"Sheet '{sheet_name}' not found")
    
    def add_job_data(self, spreadsheet_id: str, sheet_name: str, job_listings: List[JobListing], append: bool = False):
        """Add job listing data to a sheet - ULTRA FAST"""
        if not self.service:
            self.authenticate()
            
        if not job_listings:
            return
            
        # ULTRA FAST: Prepare data rows with bulk operations
        rows = []
        
        # Pre-fetch all decision makers for all companies to avoid N+1 queries
        from .models import DecisionMaker
        company_ids = [job.company.id for job in job_listings]
        decision_makers = {}
        for dm in DecisionMaker.objects.filter(company_id__in=company_ids):
            if dm.company_id not in decision_makers:
                decision_makers[dm.company_id] = []
            decision_makers[dm.company_id].append(dm)
        
        for job in job_listings:
            # Get decision makers for this company (already fetched)
            company_dms = decision_makers.get(job.company.id, [])
            
            if company_dms:
                # Create a row for each decision maker
                for dm in company_dms:
                    row = [
                        job.field or '',
                        job.posted_date.strftime('%m/%d/%Y') if job.posted_date else '',
                        job.job_title or '',
                        job.company.name or '',
                        job.company.url or '',
                        job.company.company_size or '',
                        job.job_url or '',
                        job.source_portal.name if job.source_portal else '',
                        job.location or '',
                        dm.first_name or '',
                        dm.last_name or '',
                        dm.title or '',
                        dm.linkedin_url or '',
                        dm.email or '',
                        dm.phone_number or ''
                    ]
                    rows.append(row)
            else:
                # Add a row even if no decision makers, with empty DM fields
                row = [
                    job.field,
                    job.posted_date.strftime('%m/%d/%Y'),
                    job.job_title,
                    job.company.name,
                    job.company.url or '',
                    job.company.company_size or '',
                    job.job_url,
                    job.source_portal.name if job.source_portal else '',
                    job.location or '',
                    '', '', '', '', '', '' # Empty fields for decision maker
                ]
                rows.append(row)
        
        if rows:
            # For the specific client sheet, always append after row 43
            if spreadsheet_id == "1KwJ3mFWeit6K10IuXQHXiYPJUUqkTE7tSPl9pTaMhwY":
                # Start from row 44 (after row 43)
                start_row = 44
            else:
                # For other sheets, find the next empty row
                range_name = f"{sheet_name}!A:O"
                result = self.service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=range_name
                ).execute()
                start_row = len(result.get('values', [])) + 1
            
            # ULTRA FAST: Batch update with larger chunks
            batch_size = 100  # Process in batches of 100 rows
            for i in range(0, len(rows), batch_size):
                batch_rows = rows[i:i + batch_size]
                self.service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"{sheet_name}!A{start_row + i}:O{start_row + i + len(batch_rows) - 1}",
                    valueInputOption='RAW',
                    body={'values': batch_rows}
                ).execute()
    
    def export_jobs_to_sheets(self, job_listings: List[JobListing], spreadsheet_name: str = None) -> Dict[str, Any]:
        """Export job listings to Google Sheets with proper folder structure as per client requirements"""
        try:
            # Use the client's specific spreadsheet ID
            spreadsheet_id = "1KwJ3mFWeit6K10IuXQHXiYPJUUqkTE7tSPl9pTaMhwY"
            
            # Organize jobs by location and type as per client requirements
            # Structure: Location (UK/US) > Tech/Non-Tech > Date sheets
            organized_data = self.organize_jobs_by_structure(job_listings)
            
            # Prepare CSV data with new structure
            csv_data = self.prepare_csv_data_structured(organized_data)
            
            # Create CSV file for Google Sheets import
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"job_data_organized_{len(job_listings)}_jobs_{timestamp}.csv"
            self.save_csv_file(filename, csv_data)
            
            return {
                'success': True,
                'message': f'✅ {len(job_listings)} jobs organized and prepared for Google Sheets! File: {filename}',
                'spreadsheet_url': f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit',
                'csv_file': filename,
                'instructions': f'📋 Instructions: 1) Open {filename} 2) Select all (Ctrl+A) 3) Copy (Ctrl+C) 4) Open Google Sheet 5) Paste in appropriate location folder',
                'jobs_saved': len(job_listings),
                'organization': 'Data organized by: Location > Tech/Non-Tech > Date'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error preparing data: {str(e)}',
                'spreadsheet_url': f'https://docs.google.com/spreadsheets/d/1KwJ3mFWeit6K10IuXQHXiYPJUUqkTE7tSPl9pTaMhwY/edit'
            }
    
    def prepare_csv_data(self, job_listings: List[JobListing]) -> List[List[str]]:
        """Prepare CSV data in the exact format needed for Google Sheets"""
        rows = []
        
        # Add header row
        header = [
            'Field', 'Posted Date', 'Job Title', 'Company', 'Company URL', 
            'Company Size', 'Job Link', 'Job Portal', 'Location', 
            'First Name', 'Last Name', 'Title', 'LinkedIn', 'Email', 'Phone Number'
        ]
        rows.append(header)
        
        # Pre-fetch all decision makers for all companies to avoid N+1 queries
        from .models import DecisionMaker
        company_ids = [job.company.id for job in job_listings]
        decision_makers = {}
        for dm in DecisionMaker.objects.filter(company_id__in=company_ids):
            if dm.company_id not in decision_makers:
                decision_makers[dm.company_id] = []
            decision_makers[dm.company_id].append(dm)
        
        # Add job data rows
        for job in job_listings:
            # Get decision makers for this company (already fetched)
            company_dms = decision_makers.get(job.company.id, [])
            
            if company_dms:
                # Create a row for each decision maker
                for dm in company_dms:
                    row = [
                        job.field or '',
                        job.posted_date.strftime('%m/%d/%Y') if job.posted_date else '',
                        job.job_title or '',
                        job.company.name or '',
                        job.company.url or '',
                        job.company.company_size or '',
                        job.job_url or '',
                        job.source_portal.name if job.source_portal else '',
                        job.location or '',
                        dm.first_name or '',
                        dm.last_name or '',
                        dm.title or '',
                        dm.linkedin_url or '',
                        dm.email or '',
                        dm.phone_number or ''
                    ]
                    rows.append(row)
            else:
                # Add a row even if no decision makers, with empty DM fields
                row = [
                    job.field,
                    job.posted_date.strftime('%m/%d/%Y'),
                    job.job_title,
                    job.company.name,
                    job.company.url or '',
                    job.company.company_size or '',
                    job.job_url,
                    job.source_portal.name if job.source_portal else '',
                    job.location or '',
                    '', '', '', '', '', ''  # Empty fields for decision maker
                ]
                rows.append(row)
        
        return rows
    
    def organize_jobs_by_structure(self, job_listings: List[JobListing]) -> Dict[str, Dict[str, List[JobListing]]]:
        """Organize jobs by location and type as per client requirements"""
        organized = {}
        
        for job in job_listings:
            # Determine location (UK/US)
            location = "UK" if job.market == "UK" else "USA"
            
            # Determine type (Tech/Non-Tech)
            job_type = "Tech" if job.is_technical else "Non-Tech"
            
            # Initialize structure if not exists
            if location not in organized:
                organized[location] = {}
            if job_type not in organized[location]:
                organized[location][job_type] = []
            
            organized[location][job_type].append(job)
        
        return organized
    
    def prepare_csv_data_structured(self, organized_data: Dict[str, Dict[str, List[JobListing]]]) -> List[List[str]]:
        """Prepare CSV data with proper structure organization"""
        all_rows = []
        
        # Add header row
        header = [
            'Job_Title', 'Company', 'Company_URL', 'Company_Size', 'Market (USA/UK)',
            'Source_Job-Portal', 'Job_Link', 'Posted_Date', 'Location',
            'All Decision_Maker_Name', 'All Decision_Maker_Title', 
            'All Decision_Maker_LinkedIn', 'All Decision_Maker_Email'
        ]
        all_rows.append(header)
        
        # Process each location and type
        for location, types in organized_data.items():
            for job_type, jobs in types.items():
                # Add section header
                section_header = [f"=== {location} - {job_type} Jobs ==="]
                all_rows.append(section_header)
                
                # Process jobs in this section
                for job in jobs:
                    # Get decision makers for this company
                    decision_makers = job.company.decision_makers.all()
                    
                    if decision_makers:
                        # Create a row for each decision maker
                        for dm in decision_makers:
                            row = [
                                job.job_title or '',
                                job.company.name or '',
                                job.company_url or '',
                                job.company_size or '',
                                job.market or '',
                                job.source_job_portal.name if job.source_job_portal else '',
                                job.job_link or '',
                                job.posted_date.strftime('%m/%d/%Y') if job.posted_date else '',
                                job.location or '',
                                dm.decision_maker_name or '',
                                dm.decision_maker_title or '',
                                dm.decision_maker_linkedin or '',
                                dm.decision_maker_email or ''
                            ]
                            all_rows.append(row)
                    else:
                        # Add a row even if no decision makers
                        row = [
                            job.job_title or '',
                            job.company.name or '',
                            job.company_url or '',
                            job.company_size or '',
                            job.market or '',
                            job.source_job_portal.name if job.source_job_portal else '',
                            job.job_link or '',
                            job.posted_date.strftime('%m/%d/%Y') if job.posted_date else '',
                            job.location or '',
                            '', '', '', ''  # Empty decision maker fields
                        ]
                        all_rows.append(row)
                
                # Add empty row between sections
                all_rows.append([''])
        
        return all_rows
    
    def save_csv_file(self, filename: str, data: List[List[str]]):
        """Save data to CSV file"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(data)
        
        print(f"✅ CSV file saved: {filename}")
        print(f"📊 Total rows: {len(data)}")
        print(f"📋 Ready to copy-paste into Google Sheets!")
    
    def update_existing_sheet(self, spreadsheet_id: str, job_listings: List[JobListing]):
        """Update an existing spreadsheet with new job data"""
        if not self.service:
            self.authenticate()
        
        # Get spreadsheet info
        spreadsheet = self.service.spreadsheets().get(
            spreadsheetId=spreadsheet_id
        ).execute()
        
        sheet_names = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
        
        # Separate jobs by type
        technical_jobs = [job for job in job_listings if job.is_technical]
        non_technical_jobs = [job for job in job_listings if not job.is_technical]
        
        # Add to appropriate sheets
        if technical_jobs and "Technical Jobs" in sheet_names:
            self.add_job_data(spreadsheet_id, "Technical Jobs", technical_jobs)
        
        if non_technical_jobs and "Non-Technical Jobs" in sheet_names:
            self.add_job_data(spreadsheet_id, "Non-Technical Jobs", non_technical_jobs)


def export_to_google_sheets(job_listings: List[JobListing], spreadsheet_name: str = None) -> Dict[str, Any]:
    """Convenience function to export jobs to Google Sheets"""
    service = GoogleSheetsService()
    return service.export_jobs_to_sheets(job_listings, spreadsheet_name)


def update_google_sheet(spreadsheet_id: str, job_listings: List[JobListing]):
    """Convenience function to update existing Google Sheet"""
    service = GoogleSheetsService()
    service.update_existing_sheet(spreadsheet_id, job_listings)
