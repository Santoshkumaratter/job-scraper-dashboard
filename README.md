# 🚀 Automated Job Data Scraping System

A comprehensive Django-based job scraping application that automatically collects job listings from 35+ job portals with decision maker details and Google Sheets integration.

## ✨ Features

### 🔍 Comprehensive Job Scraping
- **35+ Job Portals**: Indeed UK, LinkedIn Jobs, CV-Library, Adzuna, Totaljobs, Reed, Talent, Glassdoor, ZipRecruiter, and many more
- **Real-time Data Extraction**: Live scraping with working job URLs and company details
- **Decision Maker Information**: LinkedIn profiles, emails, and contact details

### 📊 User-Friendly Dashboard
- **Modern UI**: Clean, intuitive interface for non-technical users
- **Advanced Filtering**: Filter by keywords, market (USA/UK), job type, location, date range
- **Keyword Management**: Save, load, and manage search filters
- **Real-time Progress**: Live scraping progress with detailed status updates

### 📈 Data Organization
- **Structured Export**: Organized by Location > Tech/Non-Tech > Date
- **Google Sheets Integration**: Direct export to client's specific spreadsheet
- **CSV Export**: Fast download with all required fields
- **Database Storage**: Efficient storage with proper indexing

### ⚡ Performance & Automation
- **Ultra-Fast Scraping**: 2-5 minutes for comprehensive data collection
- **Background Processing**: Non-blocking scraping with progress tracking
- **Scheduled Automation**: 24-hour interval scraping
- **Bulk Operations**: Fast data export and deletion

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd job-scraper
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Populate job portals**
   ```bash
   python manage.py populate_job_portals
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the server**
   ```bash
   python manage.py runserver
   ```

## 🎯 Usage

### Starting a Scrape
1. Navigate to the dashboard
2. Click "Start Scraping" or use the job listings page
3. Enter keywords (required)
4. Select filters (market, job type, etc.)
5. Click "Start Scraping Now"
6. Monitor progress in real-time

### Managing Filters
1. Go to "Search Filters" in the navigation
2. Create new filters with specific criteria
3. Save filters for future use
4. Run scraping with saved filters

### Exporting Data
- **CSV Download**: Click "Export" button for instant download
- **Google Sheets**: Click "Save to Sheet" to open in Google Sheets
- **Organized Structure**: Data automatically organized by location and type

### Automation
- **Scheduled Scraping**: Run `python manage.py scheduled_scrape` for automated scraping
- **24-hour Intervals**: Automatically scrapes filters that haven't been updated recently
- **Background Tasks**: Use with Celery for production automation

## 📋 Data Fields

### Job Information
- **Job_Title**: The title of the job
- **Company**: The name of the hiring company
- **Company_URL**: The website link to the company
- **Company_Size**: The size of the company
- **Market (USA/UK)**: The market of the job posting
- **Source_Job-Portal**: The name of the job portal
- **Job_Link**: The URL for the job listing
- **Posted_Date**: The date the job was posted
- **Location**: The location of the job

### Decision Maker Information
- **All Decision_Maker_Name**: The name of the decision maker
- **All Decision_Maker_Title**: The title of the decision maker
- **All Decision_Maker_LinkedIn**: LinkedIn profile URL
- **All Decision_Maker_Email**: Email address

## 🔧 Configuration

### Google Sheets Integration
- Update the spreadsheet ID in `dashboard/google_sheets_service.py`
- Ensure proper Google API credentials are configured

### Job Portals
- All 35+ job portals are automatically populated
- Modify `dashboard/management/commands/populate_job_portals.py` to add more

### Automation
- Configure Celery for production background tasks
- Set up cron jobs for scheduled scraping

## 📁 Project Structure

```
job-scraper/
├── dashboard/                 # Main application
│   ├── models.py             # Database models
│   ├── views.py              # View logic
│   ├── comprehensive_scraper.py  # Main scraper
│   ├── google_sheets_service.py  # Google Sheets integration
│   └── management/commands/   # Management commands
├── templates/                # HTML templates
├── static/                   # CSS, JS, images
└── requirements.txt          # Dependencies
```

## 🚀 Production Deployment

1. **Environment Variables**
   - Set `DEBUG=False`
   - Configure database settings
   - Set up Google API credentials

2. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

3. **Background Tasks**
   - Install and configure Celery
   - Set up Redis for task queue
   - Configure periodic tasks

4. **Monitoring**
   - Set up logging
   - Monitor scraping performance
   - Track error rates

## 📞 Support

For technical support or feature requests, please contact the development team.

## 📄 License

This project is proprietary software. All rights reserved.