"""
Management command to populate the database with sample data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from dashboard.models import (
    JobPortal, Company, DecisionMaker, JobListing, 
    JobCategory, SearchFilter, CustomUser
)


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create job portals
        self.create_job_portals()
        
        # Create companies with decision makers
        self.create_companies()
        
        # Create job categories
        self.create_job_categories()
        
        # Create job listings
        self.create_job_listings()
        
        # Create search filters
        self.create_search_filters()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )

    def create_job_portals(self):
        """Create job portals"""
        portals = [
            {'name': 'Indeed UK', 'url': 'https://uk.indeed.com'},
            {'name': 'Indeed US', 'url': 'https://indeed.com'},
            {'name': 'LinkedIn Jobs', 'url': 'https://linkedin.com/jobs'},
            {'name': 'Glassdoor', 'url': 'https://glassdoor.com'},
            {'name': 'Monster', 'url': 'https://monster.com'},
            {'name': 'ZipRecruiter', 'url': 'https://ziprecruiter.com'},
            {'name': 'Dice', 'url': 'https://dice.com'},
            {'name': 'AngelList', 'url': 'https://angel.co'},
            {'name': 'Remote OK', 'url': 'https://remoteok.io'},
            {'name': 'We Work Remotely', 'url': 'https://weworkremotely.com'},
        ]
        
        for portal_data in portals:
            portal, created = JobPortal.objects.get_or_create(
                name=portal_data['name'],
                defaults={'url': portal_data['url'], 'is_active': True}
            )
            if created:
                self.stdout.write(f'Created job portal: {portal.name}')

    def create_companies(self):
        """Create companies with decision makers"""
        companies_data = [
            {
                'name': 'Neo4j',
                'url': 'https://neo4j.com',
                'company_size': '501-1K',
                'industry': 'Technology',
                'decision_makers': [
                    {
                        'first_name': 'Philip',
                        'last_name': 'Rathle',
                        'title': 'CTO',
                        'email': 'philip@neo4j.com',
                        'phone_number': '+44 20 7946 0958',
                        'linkedin_url': 'https://www.linkedin.com/in/prathle/',
                        'is_primary': True
                    },
                    {
                        'first_name': 'Caroline',
                        'last_name': 'Martin',
                        'title': 'Global HR',
                        'email': 'caroline.martin@neo4j.com',
                        'phone_number': '+44 20 7946 0959',
                        'linkedin_url': 'https://www.linkedin.com/in/carolinemartinhr/',
                        'is_primary': False
                    },
                    {
                        'first_name': 'Penny',
                        'last_name': 'Stevenson',
                        'title': 'Talent Acquisition EMEA',
                        'email': 'penny.stevenson@neo4j.com',
                        'phone_number': '+44 20 7946 0960',
                        'linkedin_url': 'https://www.linkedin.com/in/penny-stevenson-81260435/',
                        'is_primary': False
                    }
                ]
            },
            {
                'name': 'Kaluza',
                'url': 'https://kaluza.com',
                'company_size': '201-500',
                'industry': 'Energy Technology',
                'decision_makers': [
                    {
                        'first_name': 'Kaija',
                        'last_name': 'Barnes',
                        'title': 'Head of Talent Acquisition',
                        'email': 'kaija.barnes@kaluza.com',
                        'phone_number': '+44 20 7946 0961',
                        'linkedin_url': 'https://www.linkedin.com/in/kaija-barnes-4114a88/',
                        'is_primary': True
                    },
                    {
                        'first_name': 'Aidan',
                        'last_name': 'Lane',
                        'title': 'CTO',
                        'email': 'aidan.lane@kaluza.com',
                        'phone_number': '+44 20 7946 0962',
                        'linkedin_url': 'https://www.linkedin.com/in/aidan-lane/',
                        'is_primary': False
                    }
                ]
            },
            {
                'name': 'iPipeline',
                'url': 'https://ipipeline.com',
                'company_size': '501-1K',
                'industry': 'Financial Technology',
                'decision_makers': [
                    {
                        'first_name': 'Steve',
                        'last_name': 'Cover',
                        'title': 'CTO',
                        'email': 'steve@coverweb.net',
                        'phone_number': '+1 215 555 0101',
                        'linkedin_url': 'https://www.linkedin.com/in/stevecover/',
                        'is_primary': True
                    },
                    {
                        'first_name': 'Calvin',
                        'last_name': 'Bates',
                        'title': 'Talent Acquisition Manager',
                        'email': 'clangdon-bates@ipipeline.com',
                        'phone_number': '+1 215 555 0102',
                        'linkedin_url': 'https://www.linkedin.com/in/calvin-langdon-bates-784a53108/',
                        'is_primary': False
                    }
                ]
            },
            {
                'name': 'Spendesk',
                'url': 'https://spendesk.com',
                'company_size': '501-1K',
                'industry': 'Fintech',
                'decision_makers': [
                    {
                        'first_name': 'Richard',
                        'last_name': 'Rosenberg',
                        'title': 'CTO',
                        'email': 'richard@spendesk.com',
                        'phone_number': '+33 1 42 86 83 00',
                        'linkedin_url': 'https://www.linkedin.com/in/richard-d-rosenberg/',
                        'is_primary': True
                    },
                    {
                        'first_name': 'Marco',
                        'last_name': 'Bassi',
                        'title': 'Head Of Engineering',
                        'email': 'marco.bassi@spendesk.com',
                        'phone_number': '+33 1 42 86 83 01',
                        'linkedin_url': 'https://www.linkedin.com/in/marcobassi/',
                        'is_primary': False
                    }
                ]
            },
            {
                'name': 'rag & bone',
                'url': 'https://rag-bone.com',
                'company_size': '201-500',
                'industry': 'Fashion',
                'decision_makers': [
                    {
                        'first_name': 'Jodi',
                        'last_name': 'Lentini',
                        'title': 'Director, VIP, PR, Talent & Brand Event',
                        'email': 'jodi.lentini@rag-bone.com',
                        'phone_number': '+1 212 555 0201',
                        'linkedin_url': 'https://www.linkedin.com/in/jodi-lentini-123456789/',
                        'is_primary': True
                    }
                ]
            }
        ]
        
        for company_data in companies_data:
            company, created = Company.objects.get_or_create(
                name=company_data['name'],
                defaults={
                    'url': company_data['url'],
                    'company_size': company_data['company_size'],
                    'industry': company_data['industry']
                }
            )
            
            if created:
                self.stdout.write(f'Created company: {company.name}')
                
                # Create decision makers
                for dm_data in company_data['decision_makers']:
                    DecisionMaker.objects.create(
                        company=company,
                        first_name=dm_data['first_name'],
                        last_name=dm_data['last_name'],
                        title=dm_data['title'],
                        email=dm_data['email'],
                        phone_number=dm_data['phone_number'],
                        linkedin_url=dm_data['linkedin_url'],
                        is_primary=dm_data['is_primary']
                    )

    def create_job_categories(self):
        """Create job categories"""
        categories = [
            {'name': 'Software Engineering', 'is_technical': True},
            {'name': 'Data Science', 'is_technical': True},
            {'name': 'DevOps', 'is_technical': True},
            {'name': 'Product Management', 'is_technical': True},
            {'name': 'Marketing', 'is_technical': False},
            {'name': 'Sales', 'is_technical': False},
            {'name': 'Human Resources', 'is_technical': False},
            {'name': 'Operations', 'is_technical': False},
        ]
        
        for cat_data in categories:
            category, created = JobCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'is_technical': cat_data['is_technical'],
                    'description': f'{cat_data["name"]} related positions'
                }
            )
            if created:
                self.stdout.write(f'Created job category: {category.name}')

    def create_job_listings(self):
        """Create job listings"""
        # Get companies and portals
        companies = Company.objects.all()
        portals = JobPortal.objects.all()
        categories = JobCategory.objects.all()
        
        if not companies.exists() or not portals.exists():
            self.stdout.write('No companies or portals found. Please run this command after creating them.')
            return
        
        # Sample job listings
        job_listings_data = [
            {
                'job_title': 'Cloud Software Engineer - Graph Analytics',
                'company_name': 'Neo4j',
                'portal_name': 'Indeed UK',
                'market': 'UK',
                'job_type': 'full_time',
                'location': 'London',
                'is_technical': True,
                'field': 'Technical',
                'description': 'We are looking for a Cloud Software Engineer to work on our graph analytics platform.',
                'posted_date': date.today() - timedelta(days=1)
            },
            {
                'job_title': 'Software Engineering Manager - Flex',
                'company_name': 'Kaluza',
                'portal_name': 'Indeed UK',
                'market': 'UK',
                'job_type': 'full_time',
                'location': 'London',
                'is_technical': True,
                'field': 'Technical',
                'description': 'Lead a team of software engineers in building flexible energy solutions.',
                'posted_date': date.today() - timedelta(days=2)
            },
            {
                'job_title': 'Experienced DevOps Engineer',
                'company_name': 'iPipeline',
                'portal_name': 'Indeed UK',
                'market': 'UK',
                'job_type': 'full_time',
                'location': 'London',
                'is_technical': True,
                'field': 'Technical',
                'description': 'Join our DevOps team to improve our infrastructure and deployment processes.',
                'posted_date': date.today() - timedelta(days=3)
            },
            {
                'job_title': 'Software Engineer, KYC & AML',
                'company_name': 'Spendesk',
                'portal_name': 'Indeed UK',
                'market': 'UK',
                'job_type': 'full_time',
                'location': 'London',
                'is_technical': True,
                'field': 'Technical',
                'description': 'Build software solutions for Know Your Customer and Anti-Money Laundering compliance.',
                'posted_date': date.today() - timedelta(days=4)
            },
            {
                'job_title': 'Operations Supervisor - Full Time',
                'company_name': 'rag & bone',
                'portal_name': 'Indeed US',
                'market': 'US',
                'job_type': 'full_time',
                'location': 'New York',
                'is_technical': False,
                'field': 'Non Technical',
                'description': 'Supervise daily operations and ensure smooth workflow in our retail operations.',
                'posted_date': date.today() - timedelta(days=5)
            }
        ]
        
        for job_data in job_listings_data:
            try:
                company = companies.get(name=job_data['company_name'])
                portal = portals.get(name=job_data['portal_name'])
                
                job_listing, created = JobListing.objects.get_or_create(
                    job_title=job_data['job_title'],
                    company=company,
                    defaults={
                        'source_portal': portal,
                        'market': job_data['market'],
                        'job_type': job_data['job_type'],
                        'location': job_data['location'],
                        'is_technical': job_data['is_technical'],
                        'field': job_data['field'],
                        'description': job_data['description'],
                        'posted_date': job_data['posted_date'],
                        'job_url': f"https://example.com/job/{job_data['job_title'].lower().replace(' ', '-')}"
                    }
                )
                
                if created:
                    self.stdout.write(f'Created job listing: {job_listing.job_title}')
                    
                    # Add categories
                    if job_data['is_technical']:
                        tech_categories = categories.filter(is_technical=True)
                        job_listing.categories.set(tech_categories[:2])
                    else:
                        non_tech_categories = categories.filter(is_technical=False)
                        job_listing.categories.set(non_tech_categories[:2])
                        
            except (Company.DoesNotExist, JobPortal.DoesNotExist) as e:
                self.stdout.write(f'Error creating job listing: {e}')

    def create_search_filters(self):
        """Create sample search filters"""
        # Get or create a user for the filters
        user, created = CustomUser.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write('Created admin user: admin@example.com / admin123')
        
        # Create search filters
        filters_data = [
            {
                'name': 'Technical Jobs - UK',
                'keywords': 'python, django, react, javascript, software engineer',
                'market': 'UK',
                'is_technical': True,
                'job_type': 'full_time',
                'date_range': 'week'
            },
            {
                'name': 'Non-Technical Jobs - US',
                'keywords': 'marketing, sales, operations, manager',
                'market': 'US',
                'is_technical': False,
                'job_type': 'full_time',
                'date_range': 'week'
            },
            {
                'name': 'Remote Jobs - All',
                'keywords': 'remote, work from home, distributed',
                'job_type': 'remote',
                'date_range': 'week'
            }
        ]
        
        for filter_data in filters_data:
            search_filter, created = SearchFilter.objects.get_or_create(
                name=filter_data['name'],
                created_by=user,
                defaults=filter_data
            )
            
            if created:
                self.stdout.write(f'Created search filter: {search_filter.name}')
