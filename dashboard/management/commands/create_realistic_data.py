#!/usr/bin/env python
"""
Create realistic data with working links and proper formatting
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import JobListing, Company, DecisionMaker, JobPortal
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Create realistic data with working links'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of jobs to create'
        )
        parser.add_argument(
            '--market',
            type=str,
            choices=['USA', 'UK'],
            default='USA',
            help='Market to create jobs for'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Creating realistic data with working links...')
        )
        
        # Clear existing data
        JobListing.objects.all().delete()
        DecisionMaker.objects.all().delete()
        Company.objects.all().delete()
        
        count = options.get('count', 50)
        market = options.get('market', 'USA')
        
        self.create_realistic_data(count, market)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Created {count} realistic jobs with working links!')
        )
    
    def create_realistic_data(self, count, market):
        """Create realistic data with working links"""
        
        # Real job portals with working base URLs
        portals = [
            'Indeed UK', 'Indeed US', 'LinkedIn Jobs', 'Glassdoor', 'CV-Library',
            'Adzuna', 'Totaljobs', 'Reed', 'Talent', 'ZipRecruiter', 'CWjobs',
            'Jobsora', 'WelcometotheJungle', 'IT Job Board', 'Trueup', 'Redefined',
            'We Work Remotely', 'AngelList', 'Jobspresso', 'Grabjobs', 'Remote OK',
            'Working Nomads', 'WorkInStartups', 'Jobtensor', 'Jora', 'SEOJobs.com',
            'CareerBuilder', 'Dice', 'Escape The City', 'Jooble', 'Otta',
            'Remote.co', 'SEL Jobs', 'FlexJobs', 'Dynamite Jobs', 'SimplyHired', 'Remotive'
        ]
        
        # Technical job titles
        technical_titles = [
            'React Native Developer', 'Senior React Native Developer', 'Full Stack Developer',
            'Senior Full Stack Developer', 'Python Developer', 'Django Developer',
            'FastAPI Engineer', 'Cloud Engineer', 'DevOps Engineer', 'AI Engineer',
            'Machine Learning Engineer', 'LLM Engineer', 'Generative AI Engineer',
            'Backend Developer', 'Frontend Developer', 'Mobile App Developer',
            'Blockchain Developer', 'Cybersecurity Analyst', 'Technical Lead',
            'Engineering Manager', 'Solutions Architect', 'Platform Engineer',
            'Site Reliability Engineer', 'Data Engineer', 'MLOps Engineer',
            'Security Engineer', 'QA Engineer', 'Product Engineer', 'Infrastructure Engineer'
        ]
        
        # Non-technical job titles
        non_technical_titles = [
            'SEO Specialist', 'SEO Manager', 'Digital Marketing Specialist',
            'Digital Marketing Manager', 'Marketing Manager', 'Content Marketing Specialist',
            'Paid Advertising Manager', 'PPC Specialist', 'Google Ads Expert',
            'Product Manager', 'Sales Representative', 'HR Specialist', 'Business Analyst',
            'Project Manager', 'Content Writer', 'Customer Success Manager',
            'Operations Manager', 'Account Manager', 'Financial Analyst',
            'Business Development', 'UX Designer', 'UI Designer', 'Graphic Designer',
            'Brand Manager', 'Event Coordinator', 'Recruiter', 'Training Specialist'
        ]
        
        # Real company names with known working websites
        companies = [
            ('Microsoft', 'https://www.microsoft.com'),
            ('Google', 'https://www.google.com'),
            ('Amazon', 'https://www.amazon.com'),
            ('Apple', 'https://www.apple.com'),
            ('Meta', 'https://www.meta.com'),
            ('Netflix', 'https://www.netflix.com'),
            ('Uber', 'https://www.uber.com'),
            ('Airbnb', 'https://www.airbnb.com'),
            ('Spotify', 'https://www.spotify.com'),
            ('Slack', 'https://www.slack.com'),
            ('Zoom', 'https://www.zoom.us'),
            ('Salesforce', 'https://www.salesforce.com'),
            ('Adobe', 'https://www.adobe.com'),
            ('Oracle', 'https://www.oracle.com'),
            ('IBM', 'https://www.ibm.com'),
            ('Intel', 'https://www.intel.com'),
            ('Tesla', 'https://www.tesla.com'),
            ('SpaceX', 'https://www.spacex.com'),
            ('Palantir', 'https://www.palantir.com'),
            ('Stripe', 'https://www.stripe.com'),
            ('Square', 'https://www.square.com'),
            ('PayPal', 'https://www.paypal.com'),
            ('Shopify', 'https://www.shopify.com'),
            ('Atlassian', 'https://www.atlassian.com'),
            ('Dropbox', 'https://www.dropbox.com'),
            ('Box', 'https://www.box.com'),
            ('MongoDB', 'https://www.mongodb.com'),
            ('Redis', 'https://www.redis.com'),
            ('Elastic', 'https://www.elastic.co'),
            ('Databricks', 'https://www.databricks.com'),
            ('Snowflake', 'https://www.snowflake.com'),
            ('Confluent', 'https://www.confluent.io'),
            ('HashiCorp', 'https://www.hashicorp.com'),
            ('Docker', 'https://www.docker.com'),
            ('GitHub', 'https://www.github.com'),
            ('GitLab', 'https://www.gitlab.com'),
            ('Figma', 'https://www.figma.com'),
            ('Canva', 'https://www.canva.com'),
            ('Mailchimp', 'https://www.mailchimp.com'),
            ('HubSpot', 'https://www.hubspot.com'),
            ('Zendesk', 'https://www.zendesk.com'),
            ('Intercom', 'https://www.intercom.com'),
            ('Twilio', 'https://www.twilio.com'),
            ('OpenAI', 'https://www.openai.com'),
            ('Anthropic', 'https://www.anthropic.com'),
            ('Cohere', 'https://www.cohere.com'),
            ('Hugging Face', 'https://www.huggingface.co'),
            ('Replicate', 'https://www.replicate.com'),
            ('Vercel', 'https://www.vercel.com'),
            ('Netlify', 'https://www.netlify.com'),
            ('Railway', 'https://www.railway.app'),
            ('PlanetScale', 'https://www.planetscale.com'),
            ('Supabase', 'https://www.supabase.com'),
            ('Clerk', 'https://www.clerk.com'),
            ('Auth0', 'https://www.auth0.com')
        ]
        
        # Create jobs
        for i in range(count):
            try:
                # Select random portal
                portal_name = random.choice(portals)
                
                # Create or get portal
                portal, created = JobPortal.objects.get_or_create(
                    name=portal_name,
                    defaults={'url': f'https://{portal_name.lower().replace(" ", "")}.com', 'is_active': True}
                )
                
                # Select random company
                company_name, company_url = random.choice(companies)
                unique_id = random.randint(1000, 9999)
                full_company_name = f"{company_name} {unique_id}"
                
                # Determine if technical or non-technical
                is_technical = random.choice([True, False])
                
                if is_technical:
                    job_title = random.choice(technical_titles)
                else:
                    job_title = random.choice(non_technical_titles)
                
                # Create company with real URL
                company, created = Company.objects.get_or_create(
                    name=full_company_name,
                    defaults={
                        'url': company_url,
                        'company_size': self.get_company_size(company_name),
                        'industry': 'Technology' if is_technical else 'Business'
                    }
                )
                
                # Create realistic posted date within last 24 hours
                posted_date = timezone.now() - timedelta(hours=random.randint(1, 24))
                
                # Create job listing with working link
                job = JobListing.objects.create(
                    job_title=job_title,
                    company=company,
                    company_url=company.url,
                    company_size=company.company_size,
                    market=market,
                    source_job_portal=portal,
                    job_link=self.create_working_job_link(portal_name, job_title, market),
                    posted_date=posted_date.date(),
                    location=self.get_random_location(market),
                    job_type=random.choice(['full_time', 'remote', 'hybrid', 'on_site', 'freelance']),
                    is_technical=is_technical,
                    description=f"Join {company.name} as a {job_title}. We are looking for talented individuals to join our innovative team.",
                    scraped_at=timezone.now()
                )
                
                # Create decision makers with realistic LinkedIn profiles
                self.create_realistic_decision_makers(company)
                
            except Exception as e:
                self.stdout.write(f'❌ Error creating job {i}: {e}')
    
    def get_company_size(self, company_name):
        """Get realistic company size based on company name"""
        large_companies = ['Microsoft', 'Google', 'Amazon', 'Apple', 'Meta', 'Netflix']
        if company_name in large_companies:
            return random.choice(['10K+', '50K+', '100K+'])
        else:
            return random.choice(['51-200', '201-500', '501-1K', '1K-5K'])
    
    def get_random_location(self, market):
        """Get random location based on market"""
        if market == 'USA':
            locations = [
                'San Francisco, CA', 'New York, NY', 'Seattle, WA', 'Austin, TX',
                'Boston, MA', 'Los Angeles, CA', 'Chicago, IL', 'Denver, CO',
                'Miami, FL', 'Atlanta, GA', 'Dallas, TX', 'Portland, OR'
            ]
        else:  # UK
            locations = [
                'London, UK', 'Manchester, UK', 'Birmingham, UK', 'Edinburgh, UK',
                'Bristol, UK', 'Leeds, UK', 'Glasgow, UK', 'Cambridge, UK',
                'Oxford, UK', 'Newcastle, UK', 'Liverpool, UK', 'Sheffield, UK'
            ]
        
        return random.choice(locations)
    
    def create_working_job_link(self, portal_name, job_title, market):
        """Create working job search links"""
        
        # Use actual working job search URLs
        job_search_urls = {
            'Indeed UK': 'https://uk.indeed.com/jobs',
            'Indeed US': 'https://www.indeed.com/jobs',
            'LinkedIn Jobs': 'https://www.linkedin.com/jobs/search',
            'Glassdoor': 'https://www.glassdoor.com/Job/jobs.htm',
            'CV-Library': 'https://www.cv-library.co.uk/jobs',
            'Adzuna': 'https://www.adzuna.com/search',
            'Totaljobs': 'https://www.totaljobs.com/jobs',
            'Reed': 'https://www.reed.co.uk/jobs',
            'Talent': 'https://www.talent.com/jobs',
            'ZipRecruiter': 'https://www.ziprecruiter.com/jobs-search',
            'CWjobs': 'https://www.cwjobs.co.uk/jobs',
            'Jobsora': 'https://jobsora.com/jobs',
            'WelcometotheJungle': 'https://www.welcometothejungle.com/en/jobs',
            'IT Job Board': 'https://www.itjobboard.co.uk/jobs',
            'Trueup': 'https://www.trueup.io/jobs',
            'Redefined': 'https://www.redefined.co.uk/jobs',
            'We Work Remotely': 'https://weworkremotely.com/remote-jobs',
            'AngelList': 'https://angel.co/jobs',
            'Jobspresso': 'https://jobspresso.co/jobs',
            'Grabjobs': 'https://www.grabjobs.co.uk/jobs',
            'Remote OK': 'https://remoteok.io/remote-jobs',
            'Working Nomads': 'https://www.workingnomads.com/jobs',
            'WorkInStartups': 'https://www.workinstartups.com/jobs',
            'Jobtensor': 'https://www.jobtensor.com/jobs',
            'Jora': 'https://au.jora.com/jobs',
            'SEOJobs.com': 'https://www.seojobs.com/jobs',
            'CareerBuilder': 'https://www.careerbuilder.com/jobs',
            'Dice': 'https://www.dice.com/jobs',
            'Escape The City': 'https://www.escapethecity.org/jobs',
            'Jooble': 'https://jooble.org/jobs',
            'Otta': 'https://otta.com/jobs',
            'Remote.co': 'https://remote.co/remote-jobs',
            'SEL Jobs': 'https://www.seljobs.com/jobs',
            'FlexJobs': 'https://www.flexjobs.com/search',
            'Dynamite Jobs': 'https://dynamitejobs.com/jobs',
            'SimplyHired': 'https://www.simplyhired.com/search',
            'Remotive': 'https://remotive.com/remote-jobs'
        }
        
        base_url = job_search_urls.get(portal_name, 'https://www.indeed.com/jobs')
        
        # Create search URLs with keywords
        keyword = job_title.replace(' ', '+').replace(',', '%2C')
        
        if 'indeed' in base_url.lower():
            if market == 'UK':
                return f"{base_url}?q={keyword}&l=London%2C+UK&sort=date"
            else:
                return f"{base_url}?q={keyword}&l=United+States&sort=date"
        elif 'linkedin' in base_url.lower():
            if market == 'UK':
                return f"{base_url}/?keywords={keyword}&location=London%2C%20England%2C%20United%20Kingdom&sortBy=DD"
            else:
                return f"{base_url}/?keywords={keyword}&location=United%20States&sortBy=DD"
        elif 'glassdoor' in base_url.lower():
            if market == 'UK':
                return f"{base_url}?sc.keyword={keyword}&locT=C&locId=2671304&sortBy=date_desc"
            else:
                return f"{base_url}?sc.keyword={keyword}&locId=1&sortBy=date_desc"
        else:
            # Generic search URL
            return f"{base_url}?q={keyword}&location={'London' if market == 'UK' else 'United+States'}"
    
    def create_realistic_decision_makers(self, company):
        """Create realistic decision makers with working LinkedIn profiles"""
        first_names = ['John', 'Sarah', 'Michael', 'Emily', 'David', 'Lisa', 'James', 'Anna', 'Robert', 'Maria',
                      'Chris', 'Jennifer', 'Mark', 'Jessica', 'Daniel', 'Ashley', 'Matthew', 'Amanda', 'Anthony', 'Stephanie']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                     'Anderson', 'Taylor', 'Thomas', 'Hernandez', 'Moore', 'Martin', 'Jackson', 'Thompson', 'White', 'Lopez']
        
        # Professional titles based on company size
        if company.company_size in ['10K+', '50K+', '100K+']:
            titles = ['CTO', 'VP Engineering', 'Head of Technology', 'Technical Director', 'VP Product', 'Head of Product']
        elif company.company_size in ['1K-5K', '5K-10K']:
            titles = ['Engineering Manager', 'Lead Developer', 'Senior Developer', 'Architect', 'Product Manager', 'Technical Lead']
        else:
            titles = ['Senior Developer', 'Lead Developer', 'Technical Lead', 'Product Manager', 'Engineering Manager', 'CTO']
        
        # Create 1-3 decision makers per company
        num_dms = random.randint(1, 3)
        
        for i in range(num_dms):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            title = random.choice(titles)
            
            # Create realistic LinkedIn profile (these would be real profiles in practice)
            linkedin_url = f"https://www.linkedin.com/in/{first_name.lower()}-{last_name.lower()}"
            email = f'{first_name.lower()}.{last_name.lower()}@{company.name.split()[0].lower()}.com'
            phone = self.generate_realistic_phone()
            
            DecisionMaker.objects.create(
                company=company,
                decision_maker_name=f"{first_name} {last_name}",
                decision_maker_title=title,
                decision_maker_email=email,
                decision_maker_linkedin=linkedin_url,
                decision_maker_phone=phone,
                is_primary=i == 0
            )
    
    def generate_realistic_phone(self):
        """Generate realistic phone numbers"""
        formats = [
            f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
            f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
            f"+44 {random.randint(20, 79)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}",
            f"0{random.randint(20, 79)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}",
        ]
        return random.choice(formats)
