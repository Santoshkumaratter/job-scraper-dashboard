from django import forms
from django.forms import ModelForm, Textarea, TextInput, Select, CheckboxInput, PasswordInput, EmailInput
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import SearchFilter, JobCategory, JobPortal

User = get_user_model()

class SearchFilterForm(ModelForm):
    class Meta:
        model = SearchFilter
        fields = ['name', 'keywords', 'market', 'job_type', 'is_technical', 'is_active', 'job_boards', 'date_range']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Tech Jobs in London'}),
            'keywords': Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter comma-separated keywords (e.g., python, django, software engineer)'
            }),
            'market': Select(attrs={'class': 'form-select'}),
            'job_type': Select(attrs={'class': 'form-select'}),
            'is_technical': Select(choices=[(None, 'All'), (True, 'Technical'), (False, 'Non-Technical')], 
                                 attrs={'class': 'form-select'}),
            'is_active': CheckboxInput(attrs={'class': 'form-check-input'}),
            'job_boards': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'date_range': Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'keywords': 'Use commas to separate multiple keywords or phrases.',
            'is_technical': 'Filter by technical or non-technical roles',
            'job_boards': 'Select specific job boards to search (leave empty to search all)',
            'date_range': 'Filter jobs by posting date',
        }

    def clean_keywords(self):
        keywords = self.cleaned_data.get('keywords', '')
        if not keywords.strip():
            raise forms.ValidationError("At least one keyword is required.")
        return keywords

class JobCategoryForm(ModelForm):
    class Meta:
        model = JobCategory
        fields = ['name', 'description', 'is_technical']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_technical': CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        widget=EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email',
            'required': 'required'
        }),
        help_text='Required. Enter a valid email address.'
    )
    first_name = forms.CharField(
        max_length=30,
        widget=TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name',
            'autocomplete': 'given-name'
        }),
        help_text='Required. 30 characters or fewer.'
    )
    last_name = forms.CharField(
        max_length=30,
        widget=TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name',
            'autocomplete': 'family-name'
        }),
        help_text='Required. 30 characters or fewer.'
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a password',
            'autocomplete': 'new-password'
        }),
        help_text=(
            'Your password must contain at least 8 characters and can\'t be entirely numeric.'
        ),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        }),
        strip=False,
        help_text='Enter the same password as before, for verification.',
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email.lower()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove default help text for username field
        self.fields['password1'].help_text = (
            'Your password must contain at least 8 characters and can\'t be entirely numeric.'
        )


class JobPortalForm(ModelForm):
    class Meta:
        model = JobPortal
        fields = ['name', 'url', 'is_active']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'url': TextInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
            'is_active': CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SingleScrapeForm(forms.Form):
    """Form for single page scraping with all required filters"""
    
    KEYWORD_TYPE_CHOICES = [
        ('Technical', 'Technical'),
        ('Non-Technical', 'Non-Technical'),
    ]
    
    MARKET_CHOICES = [
        ('USA', 'USA'),
        ('UK', 'UK'),
        ('Both', 'Both'),
    ]
    
    JOB_TYPE_CHOICES = [
        ('All', 'All'),
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
    
    TIME_RANGE_CHOICES = [
        ('24', 'Last 24 hours'),
        ('48', 'Last 48 hours'),
        ('72', 'Last 72 hours'),
        ('168', 'Last 7 days'),
        ('720', 'Last 30 days'),
    ]
    
    # Get job portals for the dropdown
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get all job portals
        job_portals = JobPortal.objects.filter(is_active=True).order_by('name')
        job_portal_choices = [('All', 'All Job Portals')]
        job_portal_choices.extend([(portal.name, portal.name) for portal in job_portals])
        
        self.fields['job_board'] = forms.ChoiceField(
            choices=job_portal_choices,
            widget=Select(attrs={'class': 'form-select'}),
            initial='All',
            help_text='Select a specific job portal or "All" to search all portals'
        )
    
    keyword_type = forms.ChoiceField(
        choices=KEYWORD_TYPE_CHOICES,
        widget=Select(attrs={'class': 'form-select'}),
        initial='Technical',
        help_text='Choose whether to search for technical or non-technical roles'
    )
    
    keywords = forms.CharField(
        max_length=500,
        widget=Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter keywords (e.g., Python Developer, SEO Specialist, Marketing Manager)'
        }),
        help_text='Enter the job titles or keywords you want to search for'
    )
    
    market = forms.ChoiceField(
        choices=MARKET_CHOICES,
        widget=Select(attrs={'class': 'form-select'}),
        initial='USA',
        help_text='Select the market to search in'
    )
    
    job_type = forms.ChoiceField(
        choices=JOB_TYPE_CHOICES,
        widget=Select(attrs={'class': 'form-select'}),
        initial='All',
        help_text='Filter by job type'
    )
    
    time_range = forms.ChoiceField(
        choices=TIME_RANGE_CHOICES,
        widget=Select(attrs={'class': 'form-select'}),
        initial='24',
        help_text='Filter jobs by posting date'
    )
    
    def clean_keywords(self):
        keywords = self.cleaned_data.get('keywords', '')
        if not keywords.strip():
            raise forms.ValidationError("Keywords are required!")
        return keywords.strip()
