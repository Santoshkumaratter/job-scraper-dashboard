from django.contrib import admin
from django.utils.html import format_html
from .models import (
    JobPortal, JobCategory, Company, DecisionMaker, 
    JobListing, SearchFilter, ScrapeLog
)

class JobPortalAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'url')
    readonly_fields = ('created_at', 'updated_at')

class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_technical', 'created_at')
    list_filter = ('is_technical', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

class DecisionMakerInline(admin.TabularInline):
    model = DecisionMaker
    extra = 1
    fields = ('decision_maker_name', 'decision_maker_title', 'decision_maker_email', 'decision_maker_linkedin', 'is_primary', 'last_verified')

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_size', 'industry', 'created_at')
    list_filter = ('company_size', 'industry', 'created_at')
    search_fields = ('name', 'url', 'linkedin_url')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [DecisionMakerInline]

class JobListingAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'company', 'market', 'job_type', 'is_technical', 'posted_date', 'source_job_portal')
    list_filter = ('market', 'job_type', 'is_technical', 'posted_date', 'source_job_portal')
    search_fields = ('job_title', 'company__name', 'description')
    readonly_fields = ('scraped_at', 'last_updated')
    filter_horizontal = ('categories',)
    date_hierarchy = 'posted_date'

class SearchFilterAdmin(admin.ModelAdmin):
    list_display = ('name', 'market', 'job_type', 'is_technical', 'is_active', 'created_by', 'created_at')
    list_filter = ('market', 'job_type', 'is_technical', 'is_active', 'created_at')
    search_fields = ('name', 'keywords', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')

class ScrapeLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'job_listings_found', 'companies_found', 'decision_makers_found', 'started_at', 'completed_at')
    list_filter = ('status', 'started_at', 'completed_at')
    readonly_fields = ('started_at', 'completed_at', 'job_listings_found', 'companies_found', 'decision_makers_found')
    search_fields = ('filter_used__name', 'error_message')
    date_hierarchy = 'started_at'

# Register models with their admin classes
admin.site.register(JobPortal, JobPortalAdmin)
admin.site.register(JobCategory, JobCategoryAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(JobListing, JobListingAdmin)
admin.site.register(SearchFilter, SearchFilterAdmin)
admin.site.register(ScrapeLog, ScrapeLogAdmin)
