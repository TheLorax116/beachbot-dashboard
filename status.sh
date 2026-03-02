#!/bin/bash

echo "=== Dashboard Status ==="
echo ""

# Check if process is running
if pgrep -f "streamlit run dashboard/app.py" > /dev/null; then
    PID=$(pgrep -f "streamlit run dashboard/app.py")
    echo "✅ Dashboard is RUNNING (PID: $PID)"
    
    # Get process info
    ps -p $PID -o %cpu,%mem,etime | tail -n 1
else
    echo "❌ Dashboard is NOT running"
fi

echo ""

# Check port
if netstat -tlnp 2>/dev/null | grep :8501 > /dev/null; then
    echo "✅ Port 8501 is LISTENING"
else
    echo "❌ Port 8501 is NOT listening"
fi

echo ""

# Check logs
if [ -f logs/dashboard.log ]; then
    echo "Last 5 log entries:"
    tail -5 logs/dashboard.log
else
    echo "No log file found"
fi

echo ""
echo "To start: ./start.sh"
echo "To stop: ./stop.sh"
echo "To view logs: tail -f logs/dashboard.log"
