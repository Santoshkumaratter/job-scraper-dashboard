"""
Company URL and size utilities
Provides functions to dynamically generate realistic company URLs, sizes, and industries
"""

import random
import re
from typing import Dict, Any, Optional, Tuple, List

def get_company_url(company_name: str) -> str:
    """Dynamically generate company URL from company name"""
    # Clean up company name for URL
    clean_name = company_name.lower()
    
    # Replace spaces, apostrophes, and hyphens
    clean_name = re.sub(r'[^\w\s]', '', clean_name)
    clean_name = re.sub(r'\s+', '', clean_name)
    
    # Remove common business suffixes
    suffixes = ['inc', 'llc', 'ltd', 'corp', 'corporation', 'group', 'holdings', 
               'technologies', 'solutions', 'systems', 'international', 'worldwide',
               'global', 'enterprises', 'company', 'co', 'partners', 'associates']
    
    for suffix in suffixes:
        if clean_name.endswith(suffix):
            clean_name = clean_name[:-len(suffix)]
    
    # Generate URL with various TLDs weighted by popularity
    tlds = ['.com'] * 60 + ['.io'] * 10 + ['.co'] * 10 + ['.ai'] * 5 + ['.org'] * 5 + ['.net'] * 5 + ['.tech'] * 3 + ['.dev'] * 2
    tld = random.choice(tlds)
    
    # Different URL formats
    url_formats = [
        f"https://www.{clean_name}{tld}",
        f"https://{clean_name}{tld}",
        f"https://get{clean_name}{tld}",
        f"https://{clean_name}hq{tld}",
        f"https://www.{clean_name}app{tld}",
    ]
    
    # Choose format with weighted probability
    weights = [0.7, 0.1, 0.05, 0.05, 0.1]
    selected_format = random.choices(url_formats, weights=weights, k=1)[0]
    
    return selected_format

def get_company_size_range(company_name: str) -> Tuple[int, int]:
    """Get numeric company size range based on company name pattern analysis"""
    # Look for keywords that might indicate size
    name_lower = company_name.lower()
    
    # Identify potential enterprise companies
    enterprise_indicators = ['global', 'international', 'worldwide', 'holdings', 'group', 'corp']
    # Identify potential startups
    startup_indicators = ['labs', 'ai', 'tech', 'digital', 'innovations', 'io', 'robotics', 
                         'crypto', 'blockchain', 'systems', 'software', 'analytics']
    # Identify potential small businesses
    smb_indicators = ['services', 'consulting', 'agency', 'studio', 'partners', 'associates']
    
    # Count indicators in name
    enterprise_count = sum(1 for word in enterprise_indicators if word in name_lower)
    startup_count = sum(1 for word in startup_indicators if word in name_lower)
    smb_count = sum(1 for word in smb_indicators if word in name_lower)
    
    # Word length may correlate with company age/size
    length = len(company_name.split())
    
    # Calculate a size score 
    base_score = random.randint(1, 10)  # Random baseline
    size_score = base_score + enterprise_count*3 - smb_count*2 + startup_count*1
    
    if size_score < 3:
        return (1, 50)  # Very small
    elif size_score < 5:
        return (11, 200)  # Small
    elif size_score < 7:
        return (201, 1000)  # Medium
    elif size_score < 9:
        return (1001, 5000)  # Large
    else:
        return (5001, 50000)  # Enterprise

def get_company_size(company_name: str) -> str:
    """Get company size from company name using pattern analysis"""
    # Get size range
    min_size, max_size = get_company_size_range(company_name)
    
    # Standard size brackets
    size_brackets = [
        '1-10', '11-50', '51-200', '201-500', '501-1000', 
        '1001-5000', '5001-10000', '10000+'
    ]
    
    # Find appropriate bracket
    for bracket in size_brackets:
        if '-' in bracket:
            low, high = map(int, bracket.split('-'))
            if min_size <= low and max_size >= high:
                return bracket
        elif bracket.endswith('+'):
            low = int(bracket[:-1])
            if min_size >= low:
                return bracket
    
    # Weighted distribution as fallback
    sizes = []
    # Small companies (40%)
    sizes.extend(['1-10', '11-50', '51-200'] * 40)
    # Medium companies (30%)
    sizes.extend(['201-500', '501-1000'] * 30)
    # Large companies (20%)
    sizes.extend(['1001-5000'] * 20)
    # Very large companies (10%)
    sizes.extend(['5001-10000', '10000+'] * 10)
    
    return random.choice(sizes)

def infer_industry_from_name(company_name: str) -> List[str]:
    """Infer possible industries from company name"""
    name_lower = company_name.lower()
    words = set(re.findall(r'\w+', name_lower))
    
    # Industry keyword mappings
    industry_keywords = {
        'Technology': ['tech', 'software', 'digital', 'cyber', 'systems', 'solutions', 'code', 'data', 'info'],
        'AI & ML': ['ai', 'machine', 'learning', 'neural', 'intelligence', 'deep', 'cognitive'],
        'Finance': ['finance', 'capital', 'bank', 'invest', 'wealth', 'money', 'financial', 'pay'],
        'Healthcare': ['health', 'care', 'medical', 'pharma', 'bio', 'life', 'therapeutic', 'clinic'],
        'Marketing': ['marketing', 'market', 'media', 'ads', 'advertising', 'seo', 'brand', 'content'],
        'E-commerce': ['shop', 'commerce', 'retail', 'buy', 'store', 'goods', 'marketplace'],
        'Education': ['edu', 'learn', 'academy', 'school', 'university', 'college', 'training'],
        'Manufacturing': ['mfg', 'manufacturing', 'factory', 'production', 'industrial', 'make'],
        'Consulting': ['consult', 'consulting', 'advisory', 'partners', 'associates', 'group'],
        'Real Estate': ['realty', 'property', 'estate', 'housing', 'home', 'land', 'space'],
        'Energy': ['energy', 'power', 'solar', 'renewable', 'electric', 'oil', 'gas'],
        'Transportation': ['transport', 'logistics', 'delivery', 'shipping', 'freight', 'fleet'],
        'Hospitality': ['hotel', 'hospitality', 'travel', 'tourism', 'leisure', 'vacation'],
        'Media & Entertainment': ['media', 'entertainment', 'game', 'gaming', 'stream', 'video', 'audio', 'music'],
        'Food & Beverage': ['food', 'beverage', 'restaurant', 'catering', 'kitchen', 'meal', 'drink'],
    }
    
    # Score each industry based on keyword matches
    industry_scores = {}
    for industry, keywords in industry_keywords.items():
        score = sum(1 for keyword in keywords if any(keyword in word for word in words))
        if score > 0:
            industry_scores[industry] = score
    
    # If no specific matches, default to general categories
    if not industry_scores:
        return ['Technology', 'Business Services']
    
    # Return top matching industries
    sorted_industries = sorted(industry_scores.items(), key=lambda x: x[1], reverse=True)
    return [industry for industry, score in sorted_industries[:2]]

def get_company_industry(company_name: str) -> str:
    """Get company industry from company name using keyword analysis"""
    possible_industries = infer_industry_from_name(company_name)
    
    # If multiple industries were inferred, either combine them or pick one
    if len(possible_industries) > 1:
        # 50% chance to combine, 50% chance to pick one
        if random.random() < 0.5:
            return ' & '.join(possible_industries[:2])
        else:
            return possible_industries[0]
    elif possible_industries:
        return possible_industries[0]
    
    # Fallback to general industries
    general_industries = [
        'Technology',
        'Software Development',
        'Information Technology',
        'Financial Services',
        'Healthcare',
        'Retail',
        'E-commerce',
        'Marketing',
        'Consulting',
        'Manufacturing',
        'Education',
        'Telecommunications',
        'Media',
        'Entertainment',
        'Hospitality',
        'Transportation',
        'Real Estate',
        'Construction',
        'Energy',
        'Agriculture'
    ]
    
    return random.choice(general_industries)