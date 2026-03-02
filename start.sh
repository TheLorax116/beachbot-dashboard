#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."  # Go to optimized_bot directory

# Activate virtual environment
source polymarket_venv/bin/activate

# Kill any existing streamlit processes
pkill -f streamlit

# Start the dashboard
echo "Starting dashboard on port 8501..."
nohup streamlit run dashboard/app.py \
    --server.address 0.0.0.0 \
    --server.port 8501 \
    --server.headless true \
    --browser.gatherUsageStats false \
    > dashboard/logs/dashboard.log 2>&1 &

echo "Dashboard started! Check logs: tail -f dashboard/logs/dashboard.log"
echo "Access at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8501"
