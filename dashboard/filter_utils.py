"""
Filter utilities for job scraper dashboard
Provides functionality for filtering job listings
"""

from datetime import datetime, timedelta
from django.db.models import Q
from .models import JobListing, JobPortal, SearchFilter
from .keyword_categorizer import KeywordCategorizer

class JobFilterManager:
    """Manager class for handling job listing filters"""
    
    def __init__(self):
        self.categorizer = KeywordCategorizer()
    
    def apply_filters(self, queryset, filter_params):
        """
        Apply filters to job listing queryset
    
    Args:
            queryset: Initial queryset of JobListing objects
            filter_params: Dictionary of filter parameters
    
    Returns:
            Filtered queryset
        """
        # Start with the provided queryset
        filtered_qs = queryset
        
        # Apply market filter (USA/UK)
        if 'market' in filter_params and filter_params['market']:
            filtered_qs = filtered_qs.filter(market=filter_params['market'])
        
        # Apply job type filter
        if 'job_type' in filter_params and filter_params['job_type'] and filter_params['job_type'] != 'All':
            filtered_qs = filtered_qs.filter(job_type=filter_params['job_type'])
        
        # Apply technical/non-technical filter
        if 'is_technical' in filter_params and filter_params['is_technical'] is not None:
            filtered_qs = filtered_qs.filter(is_technical=filter_params['is_technical'])
        
        # Apply date range filter
        if 'date_range' in filter_params and filter_params['date_range']:
            days = self._get_days_from_range(filter_params['date_range'])
            if days is not None:
                cutoff_date = datetime.now().date() - timedelta(days=days)
                filtered_qs = filtered_qs.filter(posted_date__gte=cutoff_date)
        
        # Apply job portal filter
        if 'job_boards' in filter_params and filter_params['job_boards']:
            filtered_qs = filtered_qs.filter(source_job_portal__in=filter_params['job_boards'])
        
        # Apply keyword search
        if 'keywords' in filter_params and filter_params['keywords']:
            keywords = self._parse_keywords(filter_params['keywords'])
            if keywords:
                keyword_filter = Q()
                for keyword in keywords:
                    keyword_filter |= (
                        Q(job_title__icontains=keyword) | 
                        Q(description__icontains=keyword)
                    )
                filtered_qs = filtered_qs.filter(keyword_filter)
        
        return filtered_qs
    
    def apply_saved_filter(self, queryset, filter_id):
        """
        Apply a saved filter to job listing queryset
        
        Args:
            queryset: Initial queryset of JobListing objects
            filter_id: ID of the saved SearchFilter
            
        Returns:
            Filtered queryset
        """
        try:
            saved_filter = SearchFilter.objects.get(pk=filter_id)
            
            # Build filter parameters from saved filter
            filter_params = {
                'market': saved_filter.market,
                'job_type': saved_filter.job_type,
                'is_technical': saved_filter.is_technical,
                'keywords': saved_filter.keywords,
                'date_range': saved_filter.date_range
            }
            
            # Add job boards
            if saved_filter.job_boards.exists():
                filter_params['job_boards'] = saved_filter.job_boards.all()
            
            # Apply filters
            return self.apply_filters(queryset, filter_params)
            
        except SearchFilter.DoesNotExist:
            return queryset
    
    def _parse_keywords(self, keywords_str):
        """
        Parse keywords string into a list
        
        Args:
            keywords_str: Comma-separated keyword string
            
        Returns:
            List of keywords
        """
        if not keywords_str:
            return []
            
        return [k.strip() for k in keywords_str.split(',') if k.strip()]
    
    def _get_days_from_range(self, date_range):
        """
        Convert date range string to number of days
        
        Args:
            date_range: Date range string ('24hours', 'week', 'month', 'all')
            
        Returns:
            Number of days, or None for 'all'
        """
        if date_range == '24hours':
            return 1
        elif date_range == 'week':
            return 7
        elif date_range == 'month':
            return 30
        elif date_range == 'all':
            return None
        
        # Try to parse as hours
        try:
            return int(date_range) // 24
        except (ValueError, TypeError):
            return None
    
    def suggest_keywords(self, is_technical=True):
        """
        Get suggested keywords for job search
        
        Args:
            is_technical: Whether to suggest technical or non-technical keywords
            
        Returns:
            List of suggested keywords
        """
        return self.categorizer.get_suggested_keywords(is_technical)
    
    def categorize_job_title(self, job_title):
        """
        Categorize a job title as technical or non-technical
        
        Args:
            job_title: The job title to categorize
            
        Returns:
            Tuple of (is_technical, confidence)
        """
        return self.categorizer.categorize_job_title(job_title)