"""
Context processors for the dashboard app.
"""
from django.conf import settings

def global_settings(request):
    """
    Add global settings to the template context.
    """
    return {
        'APP_NAME': 'Job Scraper',
        'APP_VERSION': '1.0.0',
        'DEBUG': settings.DEBUG,
        'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
    }
