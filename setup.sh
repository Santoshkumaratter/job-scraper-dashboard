#!/bin/bash

# Job Scraper Dashboard Setup Script
# This script sets up the job scraper environment

# Exit on error
set -e

# Print colored messages
print_message() {
  echo -e "\e[1;34m$1\e[0m"
}

print_error() {
  echo -e "\e[1;31m$1\e[0m"
}

print_success() {
  echo -e "\e[1;32m$1\e[0m"
}

# Check if Python 3 is installed
print_message "Checking Python installation..."
if command -v python3 &>/dev/null; then
  python_version=$(python3 --version)
  print_success "Found $python_version"
else
  print_error "Python 3 not found. Please install Python 3.8 or higher."
  exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  print_message "Creating virtual environment..."
  python3 -m venv venv
  print_success "Virtual environment created."
else
  print_message "Virtual environment already exists."
fi

# Activate virtual environment
print_message "Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate

# Install dependencies
print_message "Installing dependencies..."
pip install -r requirements.txt
print_success "Dependencies installed."

# Run database migrations
print_message "Running database migrations..."
python manage.py migrate
print_success "Database migrations complete."

# Create superuser if needed
read -p "Do you want to create a superuser? (y/n): " create_superuser
if [[ $create_superuser == "y" || $create_superuser == "Y" ]]; then
  python manage.py createsuperuser
fi

# Check Google Sheets credentials
if [ ! -f "dashboard/google_sheets_credentials.json" ]; then
  print_error "Google Sheets credentials not found!"
  print_message "Please place your google_sheets_credentials.json file in the dashboard directory."
else
  print_success "Google Sheets credentials found."
fi

# Make scheduler.py executable
print_message "Making scheduler.py executable..."
chmod +x scheduler.py
print_success "scheduler.py is now executable."

# Instructions for running the service
print_message "\nSetup complete! Here's how to run the Job Scraper:\n"
print_message "1. Run the Django development server:"
echo "   python manage.py runserver"
print_message "\n2. Run the scheduler to automate scraping:"
echo "   ./scheduler.py"
print_message "\n3. Or set up as a system service using the provided job_scraper.service file"
print_message "\nFor more information, please read the README.md file."

# Deactivate virtual environment
deactivate

print_success "\nSetup complete! 🚀"
