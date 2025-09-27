from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings

from .managers import CustomUserManager

class CustomUser(AbstractUser):
    """Custom user model that uses email as the unique identifier"""
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    # Additional fields
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(_('about me'), max_length=500, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Email verification
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    
    # Login tracking
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    
    # Account status
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    
    # Set the email as the USERNAME_FIELD
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class JobPortal(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class JobCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_technical = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{'[Tech] ' if self.is_technical else ''}{self.name}"

class Company(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)
    company_size = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=200, blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Companies'
        ordering = ['name']

    def __str__(self):
        return self.name

class DecisionMaker(models.Model):
    # Exact fields as per client requirements
    decision_maker_name = models.CharField(max_length=255, verbose_name="Decision Maker Name", default="")
    decision_maker_title = models.CharField(max_length=255, verbose_name="Decision Maker Title", default="")
    decision_maker_linkedin = models.URLField(blank=True, null=True, verbose_name="Decision Maker LinkedIn")
    decision_maker_email = models.EmailField(blank=True, null=True, verbose_name="Decision Maker Email")
    decision_maker_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Decision Maker Phone")
    
    # Additional fields for better organization
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='decision_makers')
    is_primary = models.BooleanField(default=False)
    last_verified = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def name(self):
        return self.decision_maker_name

    def __str__(self):
        return f"{self.decision_maker_name} - {self.decision_maker_title} at {self.company.name}"

class JobListing(models.Model):
    MARKET_CHOICES = [
        ('USA', 'United States'),
        ('UK', 'United Kingdom'),
    ]

    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
        ('on_site', 'On-site'),
        ('freelance', 'Freelance'),
    ]

    # Exact fields as per client requirements
    job_title = models.CharField(max_length=255, verbose_name="Job Title", default="")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_listings')
    company_url = models.URLField(blank=True, null=True, verbose_name="Company URL")
    company_size = models.CharField(max_length=100, blank=True, null=True, verbose_name="Company Size")
    market = models.CharField(max_length=3, choices=MARKET_CHOICES, verbose_name="Market (USA/UK)", default="USA")
    source_job_portal = models.ForeignKey(JobPortal, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Source Job Portal")
    job_link = models.URLField(verbose_name="Job Link", default="")
    posted_date = models.DateField(verbose_name="Posted Date")
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name="Location")
    
    # Additional fields for better organization
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_technical = models.BooleanField(default=False)
    categories = models.ManyToManyField(JobCategory, related_name='job_listings', blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_updated')

    class Meta:
        ordering = ['-posted_date', '-scraped_at']
        indexes = [
            models.Index(fields=['job_title']),
            models.Index(fields=['market']),
            models.Index(fields=['is_technical']),
            models.Index(fields=['posted_date']),
        ]

    def __str__(self):
        return f"{self.job_title} at {self.company.name}"

class SearchFilter(models.Model):
    name = models.CharField(max_length=200)
    keywords = models.TextField(help_text="Comma-separated list of keywords")
    market = models.CharField(max_length=3, choices=JobListing.MARKET_CHOICES, blank=True, null=True)
    job_type = models.CharField(max_length=20, choices=JobListing.JOB_TYPE_CHOICES, blank=True, null=True)
    is_technical = models.BooleanField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    # Add job board filter
    job_boards = models.ManyToManyField(JobPortal, blank=True, help_text="Select specific job boards to search (leave empty to search all)")
    # Add date range filter
    date_range = models.CharField(max_length=20, choices=[
        ('24hours', 'Last 24 hours'),
        ('week', 'Last 7 days'),
        ('month', 'Last 30 days'),
        ('all', 'All time')
    ], default='week')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='search_filters')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ScrapeLog(models.Model):
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    filter_used = models.ForeignKey(SearchFilter, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    job_listings_found = models.PositiveIntegerField(default=0)
    companies_found = models.PositiveIntegerField(default=0)
    decision_makers_found = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_updated')

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Scrape {self.get_status_display()} at {self.started_at}"
