#!/bin/bash
echo "=== Dashboard Status ==="
if pgrep -f "streamlit.*dashboard/app.py" > /dev/null; then
    echo "✅ Dashboard is RUNNING"
    echo "PID: $(pgrep -f streamlit)"
    echo ""
    echo "Last 5 log entries:"
    tail -5 dashboard/logs/dashboard.log
else
    echo "❌ Dashboard is NOT running"
fi
echo ""
echo "To restart: pkill -f streamlit && ./dashboard/start.sh"
