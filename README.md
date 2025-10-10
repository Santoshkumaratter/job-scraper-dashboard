# Job Scraper Dashboard

A comprehensive job scraping and dashboard system that collects detailed job listings from various job portals and stores the data in Google Sheets.

## Overview

This system allows users to scrape job listings from 36 different job portals across USA and UK markets. It extracts detailed information including job titles, companies, decision-makers, and contact information. The data is categorized and exported to Google Sheets for easy access by non-technical users.

## Features

- **Automated Job Scraping**: Scrape job data from 36 job portals including Indeed, LinkedIn, Glassdoor, and more
- **Comprehensive Data Collection**: Collects detailed job information including:
  - Job title, company, location
  - Company URL and size
  - Decision maker names, titles, LinkedIn profiles, and email addresses
- **User-Friendly Dashboard**: Simple interface for non-technical users
- **Flexible Filtering**: Filter by:
  - Market (USA/UK)
  - Job Type (remote, hybrid, full-time, etc.)
  - Technical vs. Non-Technical jobs
  - Date posted (24 hours, 3 days, 7 days)
  - Specific job portals
- **Saved Filters**: Save and load custom filters for repeated searches
- **Google Sheets Integration**: Automated export to Google Sheets
- **Scheduled Submissions**: Configured for daily submissions at specific times:
  - UK Jobs: 11:00 AM GST (Dubai time)
  - USA Jobs: 4:00 PM GST (Dubai time)

## System Requirements

- Python 3.8 or higher
- Django 5.0 or higher
- Google Sheets API credentials (for Google Sheets integration)
- Internet connection for scraping

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/job-scraper-dashboard.git
cd job-scraper-dashboard
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up Google Sheets credentials
   - Create a Google Cloud Platform project
   - Enable the Google Sheets API
   - Create a service account and download JSON credentials
   - Place the credentials in `dashboard/google_sheets_credentials.json`

5. Initialize the database
```bash
python manage.py migrate
```

6. Initialize job portals
```bash
python manage.py initialize_job_portals
```

7. Create a superuser
```bash
python manage.py createsuperuser
```

8. Run the development server
```bash
python manage.py runserver
```

## Usage

### Dashboard

1. Navigate to the dashboard at `http://localhost:8000/`
2. Log in using your credentials
3. Use the filter form to configure your search:
   - Enter job keywords (e.g., "Python Developer", "SEO Specialist")
   - Select market, job type, and other filters
   - Click "Start Scraping" to begin the job search

### Scheduled Tasks

The system includes scheduled tasks for regular job scraping and Google Sheets updates:

- **Daily Scraping**: Automatically scrapes job listings once per day
- **UK Export**: Submits UK job data at 11:00 AM GST (Dubai time)
- **USA Export**: Submits USA job data at 4:00 PM GST (Dubai time)

To set up the scheduler:
```bash
python scheduler.py
```

## Technical Details

### Components

- **ComprehensiveJobScraper**: Main scraper engine that handles job extraction
- **DecisionMakerExtractor**: Specialized component for extracting decision maker information
- **GoogleSheetsExporter**: Handles exporting data to Google Sheets
- **KeywordCategorizer**: Categorizes jobs as technical or non-technical
- **Anti-Block System**: Protection against scraper detection

### Job Portals

The system is configured to scrape from 36 job portals including:

- Indeed UK
- LinkedIn Jobs
- CV-Library
- Adzuna
- Totaljobs
- Reed
- Talent
- Glassdoor
- ZipRecruiter
- And 27 more...

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## Contact

For support or inquiries, please contact:
- Email: your.email@example.com