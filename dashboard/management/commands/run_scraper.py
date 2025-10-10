from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.comprehensive_scraper import ComprehensiveJobScraper
from dashboard.google_sheets_exporter import GoogleSheetsExporter
from dashboard.models import ScrapeLog, JobPortal

class Command(BaseCommand):
    help = 'Run job scraping with specific market and technical/non-technical preferences'

    def add_arguments(self, parser):
        parser.add_argument(
            '--market',
            type=str,
            choices=['USA', 'UK', 'both'],
            default='both',
            help='Market to scrape (USA, UK, or both)'
        )
        parser.add_argument(
            '--is_technical',
            type=str,
            choices=['true', 'false', 'both'],
            default='both',
            help='Whether to scrape technical jobs, non-technical jobs, or both'
        )
        parser.add_argument(
            '--keywords',
            type=str,
            help='Comma-separated list of keywords to search for'
        )
        parser.add_argument(
            '--hours_back',
            type=int,
            default=24,
            help='Number of hours back to search for jobs'
        )
        parser.add_argument(
            '--job_board',
            type=str,
            default='All',
            help='Specific job board to scrape, or "All" for all job boards'
        )
        parser.add_argument(
            '--export_to_sheets',
            action='store_true',
            help='Export results to Google Sheets after scraping'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting job scraper...')
        )
        
        markets = ['USA', 'UK'] if options['market'] == 'both' else [options['market']]
        
        # Parse technical/non-technical option
        if options['is_technical'] == 'both':
            technical_options = [True, False]
        elif options['is_technical'] == 'true':
            technical_options = [True]
        else:
            technical_options = [False]
            
        # Parse keywords
        keywords = options.get('keywords', '')
        
        # Process keywords that might be comma-separated
        if keywords and isinstance(keywords, str) and ',' in keywords:
            keywords = [kw.strip() for kw in keywords.split(',') if kw.strip()]
        
        # Get job board
        job_board = options.get('job_board', 'All')
        
        total_jobs = 0
        total_companies = 0
        
        scraper = ComprehensiveJobScraper()
        
        # Create ScrapeLog
        scrape_log = ScrapeLog.objects.create(
            status='started',
            started_at=timezone.now()
        )
        
        try:
            # Update status to in progress
            scrape_log.status = 'in_progress'
            scrape_log.save()
            
            # Run scraper for each combination of market and technical/non-technical
            for market in markets:
                self.stdout.write(f"Scraping for market: {market}")
                
                for is_technical in technical_options:
                    tech_status = "Technical" if is_technical else "Non-Technical"
                    self.stdout.write(f"Scraping for {tech_status} jobs...")
                    
                    jobs_created = scraper.scrape_jobs(
                        keywords=keywords,
                        market=market,
                        is_technical=is_technical,
                        hours_back=options['hours_back'],
                        job_board=job_board
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ {jobs_created} {tech_status} jobs created for {market}")
                    )
                    
                    total_jobs += jobs_created
            
            # Export to Google Sheets if requested
            if options['export_to_sheets'] and total_jobs > 0:
                self.stdout.write("Exporting to Google Sheets...")
                sheets_manager = GoogleSheetsExporter()
                
                # Export technical jobs
                if True in technical_options:
                    success, message = sheets_manager.export_technical_jobs()
                    self.stdout.write(f"Technical jobs export: {message}")
                
                # Export non-technical jobs
                if False in technical_options:
                    success, message = sheets_manager.export_non_technical_jobs()
                    self.stdout.write(f"Non-technical jobs export: {message}")
                
                # Export all jobs
                success, message = sheets_manager.export_all_jobs()
                self.stdout.write(f"All jobs export: {message}")
            
            # Update scrape log with results
            scrape_log.status = 'completed'
            scrape_log.completed_at = timezone.now()
            scrape_log.job_listings_found = total_jobs
            scrape_log.companies_found = scraper.get_companies_count()
            scrape_log.decision_makers_found = scraper.get_decision_makers_count()
            scrape_log.save()
            
            # Generate report
            portals_count = JobPortal.objects.filter(is_active=True).count()
            
            self.stdout.write(
                self.style.SUCCESS(f"""
✅ Scraping completed!
📊 Summary:
- Total jobs: {total_jobs}
- Total companies: scrape_log.companies_found
- Total decision makers: scrape_log.decision_makers_found
- Total active job portals: {portals_count}
                """)
            )
            
        except Exception as e:
            # Update scrape log with error
            scrape_log.status = 'failed'
            scrape_log.error_message = str(e)
            scrape_log.completed_at = timezone.now()
            scrape_log.save()
            
            self.stdout.write(
                self.style.ERROR(f'❌ Scraping failed: {str(e)}')
            )
            raise
