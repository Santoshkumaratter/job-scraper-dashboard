"""
Anti-blocking module for job scraper
Provides functionality to avoid detection by job sites and maintain scraping access
"""

import random
import time
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rotate_user_agent() -> str:
    """
    Returns a random user agent from a pool of modern browser agents
    """
    user_agents = [
        # Chrome Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        # Chrome MacOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        # Firefox Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
        # Firefox MacOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
        # Safari
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        # Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        # Mobile
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        ]
    
    return random.choice(user_agents)

def get_request_headers() -> Dict[str, str]:
    """
    Returns headers for HTTP requests that mimic a real browser
    """
    user_agent = rotate_user_agent()
    
    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
    }
    
    return headers

def get_proxy() -> Optional[Dict[str, str]]:
    """
    Returns a proxy configuration for requests
    In production, this would connect to a paid proxy service
    """
    # For demo purposes, we'll return None or a placeholder
    # In production, implement with a rotating proxy service
    use_proxy = random.random() < 0.3  # 30% chance to use proxy in this example
    
    if not use_proxy:
        return None
        
    # This is a placeholder. In production, you would:
    # 1. Use a paid proxy service API
    # 2. Implement proxy rotation
    # 3. Handle proxy authentication
    # 4. Monitor proxy health
    return {
        'http': 'http://proxy.example.com:8080',
        'https': 'http://proxy.example.com:8080'
    }

def add_request_delay(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
    """
    Adds a random delay between requests to avoid detection
    
    Args:
        min_seconds: Minimum delay in seconds
        max_seconds: Maximum delay in seconds
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def handle_rate_limiting(response: Any, retry_after: int = 60) -> bool:
    """
    Handles rate limiting responses
    
    Args:
        response: HTTP response object
        retry_after: Default seconds to wait if no Retry-After header
        
    Returns:
        bool: Whether to retry the request
    """
    # Check if response indicates rate limiting
    if response.status_code in (429, 503):
        # Check for Retry-After header
        retry_seconds = retry_after
        if 'Retry-After' in response.headers:
            try:
                retry_seconds = int(response.headers['Retry-After'])
            except (ValueError, TypeError):
                pass
                
        logger.warning(f"Rate limited. Waiting {retry_seconds} seconds before retry.")
        time.sleep(retry_seconds)
        return True
        
    return False

def rotate_request_patterns() -> Dict[str, Any]:
    """
    Rotates request patterns to appear more human-like
    
    Returns:
        Dict with request pattern parameters
    """
    patterns = {
        'timeout': random.uniform(10, 30),  # Timeout seconds
        'verify_ssl': random.random() > 0.05,  # 5% chance to not verify SSL
        'allow_redirects': random.random() > 0.1,  # 10% chance to not follow redirects
        'stream': random.random() < 0.3,  # 30% chance to stream
    }
    
    return patterns

def is_bot_detection_page(html_content: str) -> bool:
    """
    Detects if the response is a bot detection/captcha page
    
    Args:
        html_content: HTML content from the response
        
    Returns:
        bool: True if detected as bot detection page
    """
    bot_detection_signs = [
        'captcha', 'robot', 'automated access', 'bot check',
        'verify you are human', 'security check', 'unusual activity',
        'cloudflare', 'ddos protection', 'browser verification'
    ]
    
    html_lower = html_content.lower()
    
    for sign in bot_detection_signs:
        if sign in html_lower:
            return True
            
    return False