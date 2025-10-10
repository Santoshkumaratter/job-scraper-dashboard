#!/usr/bin/env python
"""
Scheduler for job scraper system
Manages scheduled tasks for scraping and data export
"""

import os
import sys
import time
import logging
import schedule
import subprocess
import datetime
import pytz
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MANAGE_PY = os.path.join(SCRIPT_DIR, "manage.py")

def run_command(command: str) -> bool:
    """
    Run a system command and log the output
    
    Args:
        command: The command to run
        
    Returns:
        bool: True if command succeeded, False otherwise
    """
    logger.info(f"Running command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        logger.info(f"Command output: {result.stdout}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        return False

def is_weekend() -> bool:
    """Check if today is a weekend"""
    now = datetime.datetime.now()
    return now.weekday() >= 5  # 5 = Saturday, 6 = Sunday

def get_dubai_time() -> datetime.datetime:
    """Get current time in Dubai (GST/UTC+4)"""
    dubai_tz = pytz.timezone('Asia/Dubai')
    return datetime.datetime.now(dubai_tz)

def run_daily_scraper() -> None:
    """Run daily scraping job"""
    # Skip on weekends
    if is_weekend():
        logger.info("Today is a weekend. Skipping daily scraper.")
        return
        
    logger.info("Starting daily scraping job")
    
    # Run technical jobs scraper
    command_tech = f"python {MANAGE_PY} run_scraper --market both --is_technical true --export_to_sheets"
    tech_success = run_command(command_tech)
    
    # Run non-technical jobs scraper
    command_nontech = f"python {MANAGE_PY} run_scraper --market both --is_technical false --export_to_sheets"
    nontech_success = run_command(command_nontech)
    
    if tech_success and nontech_success:
        logger.info("Daily scraping job completed successfully")
    else:
        logger.error("Daily scraping job completed with errors")

def run_uk_export() -> None:
    """Run UK export at 11:00 AM GST"""
    # Skip on weekends
    if is_weekend():
        logger.info("Today is a weekend. Skipping UK export.")
        return
        
    # Verify time is close to 11:00 AM GST
    dubai_time = get_dubai_time()
    if abs(dubai_time.hour - 11) > 1 or dubai_time.minute > 30:
        logger.warning(f"UK export should run at 11:00 AM GST, but current time is {dubai_time.strftime('%H:%M')} GST")
    
    logger.info("Starting UK export")
    
    # Run technical jobs export
    command_tech = f"python {MANAGE_PY} scheduled_export --market UK --is_technical true"
    tech_success = run_command(command_tech)
    
    # Run non-technical jobs export
    command_nontech = f"python {MANAGE_PY} scheduled_export --market UK --is_technical false"
    nontech_success = run_command(command_nontech)
    
    if tech_success and nontech_success:
        logger.info("UK export completed successfully")
    else:
        logger.error("UK export completed with errors")

def run_usa_export() -> None:
    """Run USA export at 4:00 PM GST"""
    # Skip on weekends
            if is_weekend():
        logger.info("Today is a weekend. Skipping USA export.")
        return
        
    # Verify time is close to 4:00 PM GST
    dubai_time = get_dubai_time()
    if abs(dubai_time.hour - 16) > 1 or dubai_time.minute > 30:
        logger.warning(f"USA export should run at 4:00 PM GST, but current time is {dubai_time.strftime('%H:%M')} GST")
    
    logger.info("Starting USA export")
    
    # Run technical jobs export
    command_tech = f"python {MANAGE_PY} scheduled_export --market USA --is_technical true"
    tech_success = run_command(command_tech)
    
    # Run non-technical jobs export
    command_nontech = f"python {MANAGE_PY} scheduled_export --market USA --is_technical false"
    nontech_success = run_command(command_nontech)
    
    if tech_success and nontech_success:
        logger.info("USA export completed successfully")
    else:
        logger.error("USA export completed with errors")

def main() -> None:
    """Main function to set up and run scheduler"""
    logger.info("Starting job scraper scheduler")
    
    # Schedule daily scraping at 8:00 AM GST
    schedule.every().day.at("08:00").do(run_daily_scraper)
    
    # Schedule UK export at 11:00 AM GST (weekdays only)
    schedule.every().day.at("11:00").do(run_uk_export)
    
    # Schedule USA export at 4:00 PM GST (weekdays only)
    schedule.every().day.at("16:00").do(run_usa_export)
    
    # Run scheduler
    logger.info("Scheduler started. Waiting for scheduled tasks.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
        logger.error(f"Scheduler error: {str(e)}")

if __name__ == "__main__":
    main()