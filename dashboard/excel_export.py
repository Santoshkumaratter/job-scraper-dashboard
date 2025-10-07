#!/usr/bin/env python
"""
Excel Export Module for Job Scraper
Creates properly formatted Excel files with tabs and categorization as per client requirements
"""

import pandas as pd
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime
import io
import os

from .models import JobListing, Company, DecisionMaker, JobPortal


class ExcelExporter:
    """Excel exporter that creates properly formatted files with tabs and categorization"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def export_to_excel(self, filename=None):
        """Export all jobs to Excel with proper tabs and categorization"""
        if not filename:
            filename = f"All_Jobs_{self.timestamp}.xlsx"
        
        # Create Excel writer
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            
            # Get all jobs
            jobs = JobListing.objects.all().select_related(
                'company', 'source_job_portal'
            ).prefetch_related('company__decision_makers')
            
            # Create tabs based on client requirements
            self.create_uk_technical_tab(jobs, writer)
            self.create_uk_non_technical_tab(jobs, writer)
            self.create_usa_technical_tab(jobs, writer)
            self.create_usa_non_technical_tab(jobs, writer)
            self.create_all_jobs_tab(jobs, writer)
            
            # Create individual job portal tabs
            self.create_job_portal_tabs(jobs, writer)
        
        # Prepare response
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    def create_uk_technical_tab(self, jobs, writer):
        """Create UK Technical jobs tab"""
        uk_technical_jobs = jobs.filter(market='UK', is_technical=True)
        if uk_technical_jobs.exists():
            df = self.prepare_dataframe(uk_technical_jobs)
            df.to_excel(writer, sheet_name='UK Technical', index=False)
    
    def create_uk_non_technical_tab(self, jobs, writer):
        """Create UK Non-Technical jobs tab"""
        uk_non_technical_jobs = jobs.filter(market='UK', is_technical=False)
        if uk_non_technical_jobs.exists():
            df = self.prepare_dataframe(uk_non_technical_jobs)
            df.to_excel(writer, sheet_name='UK Non-Technical', index=False)
    
    def create_usa_technical_tab(self, jobs, writer):
        """Create USA Technical jobs tab"""
        usa_technical_jobs = jobs.filter(market='USA', is_technical=True)
        if usa_technical_jobs.exists():
            df = self.prepare_dataframe(usa_technical_jobs)
            df.to_excel(writer, sheet_name='USA Technical', index=False)
    
    def create_usa_non_technical_tab(self, jobs, writer):
        """Create USA Non-Technical jobs tab"""
        usa_non_technical_jobs = jobs.filter(market='USA', is_technical=False)
        if usa_non_technical_jobs.exists():
            df = self.prepare_dataframe(usa_non_technical_jobs)
            df.to_excel(writer, sheet_name='USA Non-Technical', index=False)
    
    def create_all_jobs_tab(self, jobs, writer):
        """Create All Jobs tab"""
        df = self.prepare_dataframe(jobs)
        df.to_excel(writer, sheet_name='All Jobs', index=False)
    
    def create_job_portal_tabs(self, jobs, writer):
        """Create individual tabs for each job portal"""
        portals = JobPortal.objects.all()
        
        for portal in portals:
            portal_jobs = jobs.filter(source_job_portal=portal)
            if portal_jobs.exists():
                # Clean portal name for sheet name (Excel sheet names have limitations)
                clean_name = portal.name.replace('/', '_').replace(' ', '_')[:31]  # Max 31 chars
                df = self.prepare_dataframe(portal_jobs)
                df.to_excel(writer, sheet_name=clean_name, index=False)
    
    def prepare_dataframe(self, jobs):
        """Prepare DataFrame with all required columns as per client specifications"""
        data = []
        
        for job in jobs:
            # Get all decision makers for this company
            decision_makers = job.company.decision_makers.all()
            
            if decision_makers.exists():
                # Create a row for each decision maker
                for dm in decision_makers:
                    data.append({
                        'Field': 'Technical' if job.is_technical else 'Non-Technical',
                        'Posted Date': job.posted_date.strftime('%m/%d/%Y') if job.posted_date else '',
                        'Job Title': job.job_title,
                        'Company': job.company.name,
                        'Company URL': job.company_url or '',
                        'Company Size': job.company_size or '',
                        'Job Link': job.job_link or '',
                        'Job Portal': job.source_job_portal.name if job.source_job_portal else '',
                        'Location': job.location or '',
                        'First Name': dm.decision_maker_name.split(' ', 1)[0] if dm.decision_maker_name else '',
                        'Last Name': dm.decision_maker_name.split(' ', 1)[1] if dm.decision_maker_name and ' ' in dm.decision_maker_name else '',
                        'Title': dm.decision_maker_title or '',
                        'LinkedIn': dm.decision_maker_linkedin or '',
                        'Email': dm.decision_maker_email or '',
                        'Phone Number': dm.decision_maker_phone or '',
                        'Market': job.market,
                        'Job Type': job.get_job_type_display(),
                        'Scraped At': job.scraped_at.strftime('%m/%d/%Y %H:%M:%S') if job.scraped_at else ''
                    })
            else:
                # If no decision makers, create a row with empty decision maker fields
                data.append({
                    'Field': 'Technical' if job.is_technical else 'Non-Technical',
                    'Posted Date': job.posted_date.strftime('%m/%d/%Y') if job.posted_date else '',
                    'Job Title': job.job_title,
                    'Company': job.company.name,
                    'Company URL': job.company_url or '',
                    'Company Size': job.company_size or '',
                    'Job Link': job.job_link or '',
                    'Job Portal': job.source_job_portal.name if job.source_job_portal else '',
                    'Location': job.location or '',
                    'First Name': '',
                    'Last Name': '',
                    'Title': '',
                    'LinkedIn': '',
                    'Email': '',
                    'Phone Number': '',
                    'Market': job.market,
                    'Job Type': job.get_job_type_display(),
                    'Scraped At': job.scraped_at.strftime('%m/%d/%Y %H:%M:%S') if job.scraped_at else ''
                })
        
        return pd.DataFrame(data)
    
    def export_to_csv(self, filename=None):
        """Export to CSV format as fallback"""
        if not filename:
            filename = f"All_Jobs_{self.timestamp}.csv"
        
        jobs = JobListing.objects.all().select_related(
            'company', 'source_job_portal'
        ).prefetch_related('company__decision_makers')
        
        df = self.prepare_dataframe(jobs)
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Write CSV
        df.to_csv(response, index=False)
        
        return response
    
    def get_export_stats(self):
        """Get statistics about the export"""
        total_jobs = JobListing.objects.count()
        total_companies = Company.objects.count()
        total_decision_makers = DecisionMaker.objects.count()
        
        uk_technical = JobListing.objects.filter(market='UK', is_technical=True).count()
        uk_non_technical = JobListing.objects.filter(market='UK', is_technical=False).count()
        usa_technical = JobListing.objects.filter(market='USA', is_technical=True).count()
        usa_non_technical = JobListing.objects.filter(market='USA', is_technical=False).count()
        
        return {
            'total_jobs': total_jobs,
            'total_companies': total_companies,
            'total_decision_makers': total_decision_makers,
            'uk_technical': uk_technical,
            'uk_non_technical': uk_non_technical,
            'usa_technical': usa_technical,
            'usa_non_technical': usa_non_technical,
            'timestamp': self.timestamp
        }
