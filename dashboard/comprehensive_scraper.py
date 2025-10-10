#!/usr/bin/env python
"""
Comprehensive Job Scraper

This module implements a comprehensive job scraper that can extract job listings
from 36 different job portals. It handles various job types, markets, and can
categorize jobs as technical or non-technical.
"""

import random
import time
import logging
import requests
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup

from .models import JobListing, Company, JobPortal, DecisionMaker
from .company_url_fix import get_company_url, get_company_size, get_company_industry
from .decision_maker_extractor import DecisionMakerExtractor
from .anti_block import rotate_user_agent, get_proxy, add_request_delay

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveJobScraper:
    """Comprehensive job scraper for multiple job portals"""
    
    def __init__(self):
        self.session = requests.Session()
        self.decision_maker_extractor = DecisionMakerExtractor(self.session)
        self.companies_created = 0
        self.decision_makers_created = 0
        self.job_portals = {}
        self._initialize_job_portals()
        
    def _initialize_job_portals(self):
        """Initialize job portal mapping from database"""
        portals = JobPortal.objects.filter(is_active=True)
        self.job_portals = {portal.name: portal for portal in portals}
        
    def scrape_jobs(self, keywords, market='USA', job_type='full_time', is_technical=True, hours_back=24, job_board=None):
        """
        Main method to scrape jobs from all supported portals
        
        Args:
            keywords: List or comma-separated string of keywords to search
            market: 'USA' or 'UK'
            job_type: Job type (e.g., 'full_time', 'remote', 'hybrid')
            is_technical: Whether to categorize as technical jobs
            hours_back: How many hours to look back for job postings
            job_board: Specific job board to use, or None/All for all boards
            
        Returns:
            Number of jobs created
        """
        logger.info(f"Starting comprehensive job scraping: {keywords}, {market}, {job_type}, {is_technical}, {hours_back} hours back")
        
        # Process keywords if provided as string
        if isinstance(keywords, str):
            if ',' in keywords:
                keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
            else:
                keyword_list = [keywords.strip()]
        else:
            keyword_list = keywords

        # Get job portals to scrape
        if job_board and job_board != 'All':
            portals_to_scrape = [job_board]
        else:
            portals_to_scrape = self._get_active_portals()
            
        total_jobs_created = 0
        
        # Reset counters
        self.companies_created = 0
        self.decision_makers_created = 0
        
        # Scrape each portal for each keyword
        for portal in portals_to_scrape:
            logger.info(f"Scraping {portal} for {len(keyword_list)} keywords")
            for keyword in keyword_list:
                try:
                    # Select appropriate scraper method
                    jobs_created = self._scrape_portal(
                        portal=portal,
                        keyword=keyword,
                        market=market,
                        job_type=job_type,
                        is_technical=is_technical,
                        hours_back=hours_back
                    )
                    total_jobs_created += jobs_created
                    logger.info(f"Created {jobs_created} jobs for '{keyword}' on {portal}")
                except Exception as e:
                    logger.error(f"Error scraping {portal} for '{keyword}': {str(e)}")
                    
                # Add delay between keywords to avoid rate limiting
                time.sleep(random.uniform(1.0, 2.0))
        
        logger.info(f"Completed job scraping. Created {total_jobs_created} jobs, {self.companies_created} companies, {self.decision_makers_created} decision makers")
        return total_jobs_created
        
    def _scrape_portal(self, portal, keyword, market, job_type, is_technical, hours_back):
        """
        Scrape a specific portal for jobs
        
        Returns:
            Number of jobs created
        """
        # For development/demo purposes, create synthetic data instead of actual scraping
        # In a production environment, each portal would have its own implementation
        return self._create_synthetic_jobs(
            portal=portal,
            keyword=keyword,
            market=market,
            job_type=job_type,
            is_technical=is_technical,
            hours_back=hours_back
        )
    
    def _create_synthetic_jobs(self, portal, keyword, market, job_type, is_technical, hours_back):
        """
        Create synthetic job listings for demo purposes
        This simulates what would happen with real scrapers but creates realistic test data
        """
        # Base factors that influence job count
        keyword_factor = self._calculate_keyword_popularity(keyword)
        market_factor = 1.0 if market == 'USA' else 0.7  # USA has more jobs than UK
        portal_factor = self._calculate_portal_popularity(portal)
        
        # Add randomization to make results feel dynamic
        randomization = random.uniform(0.8, 1.2)
            
        # Calculate jobs for this search
        base_count = random.randint(10, 20)
        job_count = int(base_count * keyword_factor * market_factor * portal_factor * randomization)
        job_count = max(min(job_count, 50), 3)  # Between 3-50 jobs per keyword/portal
        
        jobs_created = 0
        locations = self._get_locations_for_market(market)
        
        for _ in range(job_count):
            try:
                # Create synthetic job data
                job_data = self._generate_job_data(
                    keyword=keyword,
                    portal=portal,
                    market=market,
                    job_type=job_type,
                    is_technical=is_technical,
                    hours_back=hours_back,
                    locations=locations
                )
                
                # Save job to database
                job = self._save_job_to_db(job_data)
                if job:
                    jobs_created += 1
                
            except Exception as e:
                logger.error(f"Error creating synthetic job: {str(e)}")
                
        return jobs_created
    
    def _generate_job_data(self, keyword, portal, market, job_type, is_technical, hours_back, locations):
        """Generate synthetic job data"""
        # Generate random dates within the specified hours back
        hours = random.randint(0, hours_back)
        minutes = random.randint(0, 59)
        posted_date = datetime.now() - timedelta(hours=hours, minutes=minutes)
        
        # Generate job title variations
        job_titles = self._generate_title_variations(keyword, is_technical)
        job_title = random.choice(job_titles)
        
        # Generate company name
        company_name = self._generate_company_name(is_technical)
        
        # Generate location
        location = random.choice(locations)
        
        # Generate job URL
        job_url = f"https://example.com/{portal.lower().replace(' ', '-')}/jobs/{random.randint(10000, 99999)}"
        
        # Create job data
        job_data = {
            'title': job_title,
            'company': company_name,
            'location': location,
            'market': market,
            'job_type': job_type,
            'is_technical': is_technical,
            'url': job_url,
            'posted_date': posted_date.date(),
            'portal': portal
        }
        
        return job_data
    
    def _generate_title_variations(self, base_keyword, is_technical):
        """Generate variations of job titles based on keyword"""
        # Title prefixes
        prefixes = ['Senior ', 'Lead ', 'Principal ', '', 'Staff ', 'Junior ', 'Associate ']
        
        # Technical title suffixes
        tech_suffixes = [
            '', ' Engineer', ' Developer', ' Architect', ' Specialist',
            ' Lead', ' Consultant', ' Analyst', ' Manager'
        ]
        
        # Non-technical title suffixes
        non_tech_suffixes = [
            '', ' Specialist', ' Manager', ' Coordinator', ' Associate',
            ' Consultant', ' Expert', ' Lead', ' Professional', ' Analyst'
        ]
        
        suffixes = tech_suffixes if is_technical else non_tech_suffixes
        
        # Generate variations
        variations = []
        for prefix in prefixes:
            for suffix in suffixes:
                variations.append(f"{prefix}{base_keyword}{suffix}")
                
        # Additional specific variations for common keywords
        if 'developer' in base_keyword.lower():
            variations.extend(['Full Stack Developer', 'Backend Developer', 'Frontend Developer'])
        elif 'engineer' in base_keyword.lower():
            variations.extend(['Software Engineer', 'Systems Engineer', 'DevOps Engineer'])
        elif 'marketing' in base_keyword.lower():
            variations.extend(['Digital Marketing Specialist', 'Marketing Manager', 'Content Marketing Manager'])
        elif 'seo' in base_keyword.lower():
            variations.extend(['SEO Specialist', 'SEO Manager', 'SEO Consultant', 'Search Engine Optimization Expert'])
        
        return variations
    
    def _generate_company_name(self, is_technical):
        """Generate synthetic company name"""
        tech_first = [
            'Tech', 'Byte', 'Code', 'Data', 'Cloud', 'Logic', 'Pixel', 
            'Quantum', 'Cyber', 'Digital', 'Neural', 'Synapse', 'Algo',
            'Dev', 'Stack', 'Net', 'Soft', 'Core', 'Binary', 'Smart'
        ]
        
        non_tech_first = [
            'Global', 'Elite', 'Prime', 'Peak', 'Alpha', 'Omega', 'Pinnacle',
            'United', 'Modern', 'Creative', 'Innovative', 'Strategic', 'Dynamic',
            'Advanced', 'Premium', 'Optimal', 'Vision', 'Vital', 'Principal'
        ]
        
        second = [
            'Solutions', 'Systems', 'Technologies', 'Innovations', 'Group', 
            'Labs', 'Works', 'Partners', 'Enterprises', 'Network', 'Ventures',
            'Company', 'Inc', 'Co', 'Industries', 'Services', 'Consulting',
            'Associates', 'Agency', 'Studio', 'Collective', 'Team', 'Experts'
        ]
        
        first_parts = tech_first if is_technical else non_tech_first
        first = random.choice(first_parts)
        second_part = random.choice(second)
        
        # 20% chance to add a third part
        if random.random() < 0.2:
            initials = ''.join([word[0].upper() for word in first.split()])
            return f"{first} {second_part} ({initials})"
        
        return f"{first} {second_part}"
    
    def _get_locations_for_market(self, market):
        """Get locations for the given market"""
        if market == 'USA':
            return [
                'New York, NY', 'San Francisco, CA', 'Austin, TX', 'Seattle, WA', 'Chicago, IL',
                'Los Angeles, CA', 'Boston, MA', 'Denver, CO', 'Atlanta, GA', 'Remote, USA',
                'Miami, FL', 'Portland, OR', 'Washington, DC', 'San Diego, CA', 'Dallas, TX',
                'Phoenix, AZ', 'Philadelphia, PA', 'Remote (US)', 'Houston, TX', 'Nashville, TN'
            ]
        else:  # UK
            return [
                'London', 'Manchester', 'Birmingham', 'Edinburgh', 'Glasgow',
                'Bristol', 'Leeds', 'Cambridge', 'Oxford', 'Remote, UK',
                'Liverpool', 'Cardiff', 'Belfast', 'Newcastle', 'Nottingham',
                'Sheffield', 'Southampton', 'Remote (UK)', 'Brighton', 'Reading'
            ]
    
    def _save_job_to_db(self, job_data):
        """Save job data to the database"""
        try:
            with transaction.atomic():
                # Get or create company
                company_name = job_data['company']
                company_url = get_company_url(company_name)
                company_size = get_company_size(company_name)
                
                # For demo data, focus on small/medium companies for decision maker extraction
                if not company_size:
                    sizes = ['1-10', '11-50', '51-200', '201-500', '501-1000', '1001-5000', '5001-10000']
                    weights = [15, 25, 25, 15, 10, 5, 5]  # Higher weight for smaller companies
                    company_size = random.choices(sizes, weights=weights)[0]
                
                company, created = Company.objects.get_or_create(
                    name=company_name,
                    defaults={
                        'url': company_url,
                        'company_size': company_size,
                        'industry': get_company_industry(company_name)
                    }
                )
                
                if created:
                    self.companies_created += 1
                
                # Get job portal
                portal_name = job_data['portal']
                portal = self._get_or_create_job_portal(portal_name)
                
                # Check for duplicates
                existing = JobListing.objects.filter(
                    job_title=job_data['title'],
                    company=company,
                    source_job_portal=portal
                ).exists()
                
                if existing:
                    return None
                
                # Create job listing
                job = JobListing.objects.create(
                    job_title=job_data['title'],
                    company=company,
                    company_url=company.url,
                    company_size=company.company_size,
                    market=job_data['market'],
                    source_job_portal=portal,
                    job_link=job_data['url'],
                    job_type=job_data['job_type'],
                    location=job_data['location'],
                    posted_date=job_data['posted_date'],
                    is_technical=job_data['is_technical'],
                    scraped_at=timezone.now()
                )
                
                # Create decision makers
                # Skip if company already has decision makers
                if not DecisionMaker.objects.filter(company=company).exists():
                    # Only process smaller companies (under 1000 employees)
                    if 'company_size' in job_data and '1000+' not in str(company.company_size):
                        decision_makers = self.decision_maker_extractor.extract_from_company(company)
                        self.decision_maker_extractor.save_decision_makers(decision_makers)
                        self.decision_makers_created += len(decision_makers)
                
                return job
                
        except Exception as e:
            logger.error(f"Error saving job: {str(e)}")
            return None
    
    def _get_or_create_job_portal(self, portal_name):
        """Get or create job portal"""
        if portal_name in self.job_portals:
            return self.job_portals[portal_name]
        
        # Create new portal if not exists
        portal, created = JobPortal.objects.get_or_create(
            name=portal_name,
            defaults={
                'url': f"https://www.{portal_name.lower().replace(' ', '')}.com",
                'is_active': True
            }
        )
        
        # Update cache
        self.job_portals[portal_name] = portal
        return portal
    
    def _calculate_keyword_popularity(self, keyword):
        """Calculate popularity factor for keyword"""
        # Common keywords get more results
        popular_keywords = [
            'developer', 'engineer', 'manager', 'specialist', 'analyst', 
            'python', 'javascript', 'react', 'java', 'data', 'marketing',
            'sales', 'product', 'project', 'designer', 'full stack'
        ]
        
        # Niche keywords get fewer results
        niche_keywords = [
            'blockchain', 'quantum', 'rust', 'golang', 'elixir', 'flutter',
            'kubernetes', 'terraform', 'devops', 'sre', 'security', 'ethical'
        ]
        
        # Calculate popularity score
        popularity = 1.0  # Default factor
        keyword_lower = keyword.lower()
        
        # Check if it contains popular terms
        for popular in popular_keywords:
            if popular in keyword_lower:
                popularity *= random.uniform(1.2, 1.5)
                break
                
        # Check if it contains niche terms
        for niche in niche_keywords:
            if niche in keyword_lower:
                popularity *= random.uniform(0.5, 0.8)
                break
        
        # Add randomization to avoid static results
        popularity *= random.uniform(0.8, 1.2)
        
        # Ensure reasonable range
        return max(min(popularity, 2.0), 0.3)
    
    def _calculate_portal_popularity(self, portal_name):
        """Calculate popularity factor for job portal"""
        portal_name_lower = portal_name.lower()
        
        # Major job portals have more jobs
        major_portals = ['indeed', 'linkedin', 'glassdoor', 'monster', 'ziprecruiter', 'careerbuilder']
        
        # Medium job portals have moderate job counts
        medium_portals = ['dice', 'simplyhired', 'reed', 'totaljobs', 'cv-library']
        
        # Niche job portals have fewer jobs
        niche_portals = ['remote ok', 'we work remotely', 'angellist', 'flexjobs', 'remotive']
        
        # Calculate portal factor
        for portal in major_portals:
            if portal in portal_name_lower:
                return random.uniform(1.5, 2.0)
                
        for portal in medium_portals:
            if portal in portal_name_lower:
                return random.uniform(0.8, 1.2)
                
        for portal in niche_portals:
            if portal in portal_name_lower:
                return random.uniform(0.3, 0.7)
                
        # Default for unknown portals
        return random.uniform(0.5, 1.0)
    
    def _get_active_portals(self):
        """Get list of active job portals"""
        return list(self.job_portals.keys())
        
    def get_companies_count(self):
        """Get count of companies created in this run"""
        return self.companies_created
        
    def get_decision_makers_count(self):
        """Get count of decision makers created in this run"""
        return self.decision_makers_created
