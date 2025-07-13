#!/bin/bash

# Get working directory
cwd=$(pwd)
echo "Current working directory: $cwd"

# Change to the script's directory
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd "$script_dir/../.." && pwd)"
echo "Project directory: $project_dir"
cd "$project_dir" || exit 1

# Load environment variables
if [ -f "$project_dir/.env" ]; then
    export $(grep -v '^#' "$project_dir/.env" | xargs)
    echo "Environment variables loaded from .env file."
else
    echo "No .env file found. Skipping environment variable loading."
fi

# Activate virtual environment if it exists
if [ -d "$project_dir/venv" ]; then
    source "$project_dir/venv/bin/activate"
    echo "Virtual environment activated."
else
    echo "No virtual environment found. Skipping activation."
fi

# Get timestamp for logging
timestamp=$(date +"%Y-%m-%d %H:%M:%S")
echo "Script started at: $timestamp"

# Run django management command to clean inactive customers
deleted_count=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer

# Calculate cutoff date (1 year ago)
cutoff_date = timezone.now() - timedelta(days=365)
print(f'Cutoff date for inactive customers: {cutoff_date}')

# Find customers with no orders since cutoff date
# Fixed query: customers with no orders OR orders older than cutoff
inactive_customers = Customer.objects.filter(
    models.Q(orders__isnull=True) | 
    models.Q(orders__created_at__lt=cutoff_date)
).distinct()

# Count before deletion
count_before = inactive_customers.count()
print(f'Number of inactive customers before deletion: {count_before}')

# Delete inactive customers
if count_before > 0:
    inactive_customers.delete()
    print(f'Deleted {count_before} inactive customers.')
else:
    print('No inactive customers to delete.')

# Print count for capture by shell
print(count_before)
" 2>/dev/null | tail -1)

# Log the result
echo "[$timestamp] Cleaned inactive customers: $deleted_count" >> "/tmp/customer_cleanup_log.txt"

# End of script
end_timestamp=$(date +"%Y-%m-%d %H:%M:%S")
echo "Script ended at: $end_timestamp"
echo "Cleanup process completed."

# Exit with success status
exit 0
