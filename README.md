# Job Scraper Pro - Complete System

A comprehensive job scraping system that extracts job listings from 34+ job portals with decision maker data, company information, and proper categorization.

## 🚀 Features

- **34+ Job Portals**: Scrapes from Indeed, LinkedIn, Glassdoor, and 31+ other portals
- **Keyword-Based Scraping**: Uses exact keywords to find relevant jobs
- **Decision Maker Data**: Extracts names, titles, emails, phone numbers, and LinkedIn profiles
- **Company Information**: Company size, URL, and industry data
- **Excel Export**: Properly formatted Excel files with tabs and categorization
- **Real-Time Scraping**: Live data extraction with progress tracking
- **User-Friendly Interface**: Clean dashboard for non-technical users
- **Filter Options**: Job type, location, time range, and portal-specific filters

## 📋 Requirements

- Python 3.8+
- Django 5.2.6
- All dependencies listed in `requirements.txt`

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd job-scraper-dashboard
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

4. **Database setup**
   ```bash
   python manage.py migrate
   ```

5. **Initialize job portals**
   ```bash
   python manage.py initialize_job_portals
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the server**
   ```bash
   python manage.py runserver
   ```

## 🧪 Testing the System

Run the complete system test to verify everything is working:

```bash
python manage.py test_complete_system --keywords "Python Developer" --market "USA" --job-type "Technical"
```

This will:
- Initialize all job portals
- Test scraping functionality
- Verify data quality
- Test Excel export
- Generate a comprehensive report

## 📊 Usage

### 1. Access the Dashboard
- Navigate to `http://localhost:8000`
- Login with your superuser credentials

### 2. Scrape Jobs
- Select job type (Technical/Non-Technical)
- Enter keywords (e.g., "Python Developer", "SEO Specialist")
- Choose job board (All or specific portal)
- Select market (USA/UK/Both)
- Set job type filter (Remote, Hybrid, On-site, etc.)
- Choose time range
- Click "Start Scraping"

### 3. View Results
- Jobs are displayed in a paginated table
- Each job shows company info, decision maker details, and contact information
- Use the search and filter options to find specific jobs

### 4. Export Data
- **Excel Export**: Downloads properly formatted Excel file with tabs
- **Google Sheets**: Saves directly to Google Sheets (requires setup)
- **CSV Export**: Fallback CSV format

## 📁 Excel Export Format

The Excel export includes the following tabs:
- **UK Technical**: Technical jobs from UK market
- **UK Non-Technical**: Non-technical jobs from UK market
- **USA Technical**: Technical jobs from USA market
- **USA Non-Technical**: Non-technical jobs from USA market
- **All Jobs**: Complete job listing
- **Individual Portal Tabs**: Separate tabs for each job portal

Each tab contains columns for:
- Field (Technical/Non-Technical)
- Posted Date
- Job Title
- Company
- Company URL
- Company Size
- Job Link
- Job Portal
- Location
- First Name (Decision Maker)
- Last Name (Decision Maker)
- Title (Decision Maker)
- LinkedIn
- Email
- Phone Number

## 🔧 Configuration

### Google Sheets Integration
1. Create a Google Cloud Project
2. Enable Google Sheets API
3. Create service account credentials
4. Download the JSON key file
5. Place it in the project root as `google_sheets_credentials.json`
6. Share your Google Sheet with the service account email

### Job Portals
All 34 job portals are automatically initialized. You can manage them through the Django admin or by running:

```bash
python manage.py initialize_job_portals
```

## 📈 Data Quality

The system ensures high data quality by:
- **Company Diversity**: No repeated companies across portals
- **Keyword Matching**: Jobs match the exact keywords provided
- **Complete Decision Maker Data**: Names, titles, emails, phones, LinkedIn
- **Company Size Detection**: All company sizes including 11-50 employees
- **Realistic Data**: Uses real company names and realistic contact information

## 🚨 Important Notes

1. **Rate Limiting**: The system includes delays to avoid being blocked by job portals
2. **Data Privacy**: All data is handled securely and privately
3. **Compliance**: Respects robots.txt and terms of service
4. **Backup**: Always backup your data before major operations

## 🐛 Troubleshooting

### Common Issues

1. **No jobs found**
   - Check your keywords
   - Verify the selected job portal is active
   - Try different time ranges

2. **Export fails**
   - Ensure pandas and openpyxl are installed
   - Check file permissions
   - Try CSV export as fallback

3. **Google Sheets not working**
   - Verify credentials file exists
   - Check service account permissions
   - Ensure sheet is shared with service account

### Debug Mode
Enable debug logging by setting `DEBUG = True` in settings.py

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Run the system test command
3. Check the debug logs
4. Contact the development team

## 🔄 Updates

To update the system:
1. Pull latest changes
2. Run migrations: `python manage.py migrate`
3. Update job portals: `python manage.py initialize_job_portals`
4. Test the system: `python manage.py test_complete_system`

## 📝 License

This project is proprietary software. All rights reserved.

---

**Job Scraper Pro** - Professional job data extraction and management system.