#!/bin/bash

# Script to run the scheduled exports at the required times (11AM GST for UK, 4PM GST for USA)
# This should be set up as a cron job to run every hour on weekdays
# Recommended cron entry: 0 * * * 1-5 /path/to/run_scheduled_exports.sh

# Move to the project directory
cd "$(dirname "$0")"

# Activate virtual environment if using one
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Current time in GST/Dubai time zone
# Assumes the server time is set correctly or using UTC
CURRENT_HOUR=$(TZ=Asia/Dubai date +%H)
CURRENT_MIN=$(TZ=Asia/Dubai date +%M)
CURRENT_DAY=$(date +%u)  # 1-7, where 1 is Monday

# Only run on weekdays (Monday-Friday)
if [ "$CURRENT_DAY" -ge 6 ]; then
    echo "Today is a weekend. Exports only run on weekdays."
    exit 0
fi

# Calculate time windows
UK_HOUR=11
USA_HOUR=16

# Check if current time is within range for UK export (11AM GST +/- 15 min)
if [ "$CURRENT_HOUR" -eq "$UK_HOUR" ] && [ "$CURRENT_MIN" -le 15 ]; then
    echo "Running UK export..."
    python manage.py scheduled_export --market=UK
fi

# Check if current time is within range for USA export (4PM GST +/- 15 min)
if [ "$CURRENT_HOUR" -eq "$USA_HOUR" ] && [ "$CURRENT_MIN" -le 15 ]; then
    echo "Running USA export..."
    python manage.py scheduled_export --market=USA
fi

# If run outside of scheduled times, just log
if [ "$CURRENT_HOUR" -ne "$UK_HOUR" ] && [ "$CURRENT_HOUR" -ne "$USA_HOUR" ]; then
    echo "Current time ($(TZ=Asia/Dubai date +%H:%M) GST) is not a scheduled export time."
    echo "Scheduled export times are: $UK_HOUR:00 (UK) and $USA_HOUR:00 (USA) GST."
fi
