"""
Browser automation for scraping JavaScript-heavy websites
Uses Playwright for browser automation
"""

import os
import time
import random
import logging
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlencode

# Initialize logger
logger = logging.getLogger("browser_automation")

# Try importing playwright
try:
    from playwright.sync_api import sync_playwright, Page, BrowserContext, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    logger.warning("Playwright not available. Browser automation will be disabled.")
    PLAYWRIGHT_AVAILABLE = False

class BrowserAutomation:
    """Browser automation using Playwright"""
    
    def __init__(self, headless=True):
        """Initialize browser automation"""
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.is_initialized = False
    
    def initialize(self):
        """Initialize the browser"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available. Cannot initialize browser.")
            return False
            
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.context = self.browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            self.page = self.context.new_page()
            self.is_initialized = True
            return True
        except Exception as e:
            logger.error(f"Error initializing browser: {str(e)}")
            self.close()
            return False
    
    def close(self):
        """Close the browser"""
        try:
            if self.context:
                self.context.close()
                self.context = None
                
            if self.browser:
                self.browser.close()
                self.browser = None
                
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
                
            self.is_initialized = False
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
    
    def navigate(self, url: str, timeout: int = 30000) -> bool:
        """Navigate to a URL"""
        if not self.is_initialized and not self.initialize():
            return False
            
        try:
            self.page.goto(url, timeout=timeout, wait_until='networkidle')
            time.sleep(random.uniform(1, 3))  # Wait for any dynamic content to load
            return True
        except Exception as e:
            logger.error(f"Error navigating to {url}: {str(e)}")
            return False
    
    def get_page_content(self) -> str:
        """Get the current page content"""
        if not self.is_initialized:
            return ""
            
        try:
            return self.page.content()
        except Exception as e:
            logger.error(f"Error getting page content: {str(e)}")
            return ""
    
    def wait_for_selector(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for a selector to be available on the page"""
        if not self.is_initialized:
            return False
            
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            logger.error(f"Error waiting for selector {selector}: {str(e)}")
            return False
    
    def extract_data_from_page(self, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract data from the page using selectors"""
        if not self.is_initialized:
            return {}
            
        result = {}
        
        for key, selector in selectors.items():
            try:
                elements = self.page.query_selector_all(selector)
                if elements:
                    result[key] = [elem.text_content().strip() for elem in elements]
                else:
                    result[key] = []
            except Exception as e:
                logger.error(f"Error extracting {key} using selector {selector}: {str(e)}")
                result[key] = []
        
        return result
    
    def click(self, selector: str) -> bool:
        """Click on an element"""
        if not self.is_initialized:
            return False
            
        try:
            self.page.click(selector)
            time.sleep(random.uniform(0.5, 1.5))  # Wait for any action to complete
            return True
        except Exception as e:
            logger.error(f"Error clicking on {selector}: {str(e)}")
            return False
    
    def type_text(self, selector: str, text: str) -> bool:
        """Type text into an input field"""
        if not self.is_initialized:
            return False
            
        try:
            self.page.fill(selector, text)
            time.sleep(random.uniform(0.5, 1.5))  # Wait for any action to complete
            return True
        except Exception as e:
            logger.error(f"Error typing text into {selector}: {str(e)}")
            return False
    
    def scroll_down(self, distance: int = None) -> bool:
        """Scroll down the page"""
        if not self.is_initialized:
            return False
            
        try:
            if distance:
                self.page.evaluate(f"window.scrollBy(0, {distance});")
            else:
                self.page.evaluate("window.scrollBy(0, window.innerHeight);")
            time.sleep(random.uniform(0.3, 1.0))  # Wait for loading
            return True
        except Exception as e:
            logger.error(f"Error scrolling down: {str(e)}")
            return False
    
    def scroll_to_bottom(self, max_scrolls: int = 10) -> bool:
        """Scroll to the bottom of the page"""
        if not self.is_initialized:
            return False
            
        try:
            prev_height = 0
            for _ in range(max_scrolls):
                curr_height = self.page.evaluate("document.body.scrollHeight")
                if curr_height == prev_height:
                    break
                    
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1.0, 2.0))  # Wait for content to load
                prev_height = curr_height
                
            return True
        except Exception as e:
            logger.error(f"Error scrolling to bottom: {str(e)}")
            return False
    
    def take_screenshot(self, path: str) -> bool:
        """Take a screenshot of the current page"""
        if not self.is_initialized:
            return False
            
        try:
            self.page.screenshot(path=path)
            return True
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return False
    
    def load_cookies(self, cookies: List[Dict[str, Any]]) -> bool:
        """Load cookies into the browser"""
        if not self.is_initialized:
            return False
            
        try:
            self.context.add_cookies(cookies)
            return True
        except Exception as e:
            logger.error(f"Error loading cookies: {str(e)}")
            return False
    
    def save_cookies(self) -> List[Dict[str, Any]]:
        """Save cookies from the browser"""
        if not self.is_initialized:
            return []
            
        try:
            return self.context.cookies()
        except Exception as e:
            logger.error(f"Error saving cookies: {str(e)}")
            return []

    def extract_linkedin_jobs(self, keywords: str, location: str = "United States", days: int = 1) -> List[Dict[str, Any]]:
        """
        Extract job listings from LinkedIn Jobs
        
        Args:
            keywords: Keywords to search for
            location: Location to search in
            days: Number of days to look back (1 = 24 hours, 7 = week)
        
        Returns:
            List of job listings
        """
        if not self.is_initialized and not self.initialize():
            logger.error("Browser not initialized and failed to initialize")
            return []
            
        # Map days to LinkedIn time filter values
        time_filter = "r86400" # 24 hours default
        if days == 7:
            time_filter = "r604800"
        elif days == 30:
            time_filter = "r2592000"
        
        # Build search URL
        params = {
            'keywords': keywords,
            'location': location,
            'f_TPR': time_filter,  # Time filter
            'sortBy': 'DD',        # Sort by date (most recent first)
        }
        search_url = f"https://www.linkedin.com/jobs/search/?{urlencode(params)}"
        
        logger.info(f"LinkedIn scraping: {search_url}")
        
        try:
            # Navigate to search URL
            if not self.navigate(search_url):
                logger.error("Failed to navigate to LinkedIn search URL")
                return []
                
            # Wait for job results to load
            if not self.wait_for_selector(".jobs-search__results-list", timeout=30000):
                logger.error("LinkedIn jobs didn't load")
                return []
            
            # Scroll down to load more jobs (LinkedIn loads them as you scroll)
            for _ in range(5):
                self.scroll_down()
                time.sleep(random.uniform(1.0, 2.0))
                
            # Extract job cards
            job_cards = self.page.query_selector_all("li.jobs-search-results__list-item")
            
            if not job_cards:
                logger.warning("No job cards found on LinkedIn")
                return []
                
            logger.info(f"Found {len(job_cards)} LinkedIn job cards")
            
            # Extract job data
            jobs = []
            for card in job_cards[:30]:  # Process first 30 jobs
                try:
                    # Get basic job info
                    title_elem = card.query_selector(".base-search-card__title")
                    company_elem = card.query_selector(".base-search-card__subtitle")
                    location_elem = card.query_selector(".job-search-card__location")
                    link_elem = card.query_selector("a.base-card__full-link")
                    
                    if not all([title_elem, company_elem, location_elem, link_elem]):
                        continue
                        
                    title = title_elem.text_content().strip()
                    company = company_elem.text_content().strip()
                    location = location_elem.text_content().strip()
                    job_url = link_elem.get_attribute("href")
                    
                    # Click on job to load details
                    try:
                        link_elem.click()
                        time.sleep(random.uniform(1.5, 3.0))
                    except:
                        # Skip if we can't click
                        continue
                    
                    # Extract more details from the job panel
                    job_description = ""
                    desc_elem = self.page.query_selector(".jobs-description")
                    if desc_elem:
                        job_description = desc_elem.inner_text().strip()
                    
                    # Get posted date
                    date_elem = self.page.query_selector(".jobs-unified-top-card__posted-date")
                    posted_date = date_elem.text_content().strip() if date_elem else ""
                    
                    # Get job type
                    job_type = ""
                    job_type_elem = self.page.query_selector(".jobs-unified-top-card__job-insight:has-text('Employment type')")
                    if job_type_elem:
                        job_type = job_type_elem.text_content().strip().replace("Employment type", "").strip()
                    
                    # Determine job type category
                    job_type_category = "full_time"
                    if job_type:
                        if "remote" in job_type.lower():
                            job_type_category = "remote"
                        elif "hybrid" in job_type.lower():
                            job_type_category = "hybrid"
                        elif "contract" in job_type.lower() or "freelance" in job_type.lower():
                            job_type_category = "freelance"
                    
                    # Create job object
                    job = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'url': job_url,
                        'description': job_description,
                        'posted_date': posted_date,
                        'job_type': job_type_category,
                        'source': 'LinkedIn Jobs'
                    }
                    
                    jobs.append(job)
                    
                except Exception as e:
                    logger.error(f"Error extracting LinkedIn job: {str(e)}")
                    continue
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error in LinkedIn job extraction: {str(e)}")
            return []
        finally:
            # Make sure to close browser when done
            self.close()

def scrape_linkedin_jobs(keywords: str, location: str = "United States", days: int = 1) -> List[Dict[str, Any]]:
    """
    Helper function to scrape LinkedIn jobs
    
    Args:
        keywords: Keywords to search for
        location: Location to search in
        days: Number of days to look back
        
    Returns:
        List of job listings
    """
    if not PLAYWRIGHT_AVAILABLE:
        logger.error("Playwright not available. Cannot scrape LinkedIn.")
        return []
        
    automation = BrowserAutomation(headless=True)
    return automation.extract_linkedin_jobs(keywords, location, days)
