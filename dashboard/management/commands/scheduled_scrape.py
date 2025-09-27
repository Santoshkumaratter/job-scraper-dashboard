from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from dashboard.models import SearchFilter, ScrapeLog
from dashboard.comprehensive_scraper import ComprehensiveJobScraper

class Command(BaseCommand):
    help = 'Run scheduled scraping for active filters'

    def add_arguments(self, parser):
        parser.add_argument(
            '--filter-id',
            type=int,
            help='Run scraping for a specific filter ID',
        )
        parser.add_argument(
            '--all-filters',
            action='store_true',
            help='Run scraping for all active filters',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting scheduled scraping...')
        )

        if options['filter_id']:
            # Run for specific filter
            try:
                search_filter = SearchFilter.objects.get(
                    id=options['filter_id'],
                    is_active=True
                )
                self.run_scrape_for_filter(search_filter)
            except SearchFilter.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Filter with ID {options["filter_id"]} not found or inactive')
                )
                return

        elif options['all_filters']:
            # Run for all active filters
            active_filters = SearchFilter.objects.filter(is_active=True)
            
            if not active_filters.exists():
                self.stdout.write(
                    self.style.WARNING('No active filters found')
                )
                return

            for search_filter in active_filters:
                self.run_scrape_for_filter(search_filter)

        else:
            # Default: run for filters that haven't been scraped in the last 24 hours
            yesterday = timezone.now() - timedelta(hours=24)
            
            # Get filters that need scraping (haven't been scraped recently)
            filters_to_scrape = SearchFilter.objects.filter(
                is_active=True
            ).exclude(
                scrape_logs__started_at__gte=yesterday
            ).distinct()

            if not filters_to_scrape.exists():
                self.stdout.write(
                    self.style.SUCCESS('All active filters have been scraped recently')
                )
                return

            for search_filter in filters_to_scrape:
                self.run_scrape_for_filter(search_filter)

        self.stdout.write(
            self.style.SUCCESS('✅ Scheduled scraping completed!')
        )

    def run_scrape_for_filter(self, search_filter):
        """Run scraping for a specific filter"""
        self.stdout.write(f'🔍 Scraping with filter: {search_filter.name}')
        
        # Create scrape log
        scrape_log = ScrapeLog.objects.create(
            filter_used=search_filter,
            status='started',
            started_at=timezone.now()
        )

        try:
            # Update status to in progress
            scrape_log.status = 'in_progress'
            scrape_log.save()

            # Parse keywords
            keywords = search_filter.keywords.split(',') if search_filter.keywords else []
            keywords_str = ','.join([kw.strip() for kw in keywords])

            # Run comprehensive scraping
            scraper = ComprehensiveJobScraper()
            jobs_created = scraper.scrape_jobs(
                keywords=keywords_str,
                market=search_filter.market or 'USA',
                job_type=search_filter.job_type or 'full_time',
                is_technical=search_filter.is_technical if search_filter.is_technical is not None else True,
                hours_back=24
            )

            # Update scrape log with results
            scrape_log.status = 'completed'
            scrape_log.completed_at = timezone.now()
            scrape_log.job_listings_found = jobs_created
            scrape_log.companies_found = scraper.get_companies_count()
            scrape_log.decision_makers_found = scraper.get_decision_makers_count()
            scrape_log.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Filter "{search_filter.name}": {jobs_created} jobs created'
                )
            )

        except Exception as e:
            # Update scrape log with error
            scrape_log.status = 'failed'
            scrape_log.error_message = str(e)
            scrape_log.completed_at = timezone.now()
            scrape_log.save()

            self.stdout.write(
                self.style.ERROR(
                    f'❌ Filter "{search_filter.name}" failed: {str(e)}'
                )
            )
