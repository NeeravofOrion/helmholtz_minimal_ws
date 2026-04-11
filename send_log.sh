#!/bin/bash

# ==========================================
# CONFIGURATION
# ==========================================
# Put your LAPTOP'S username here!
LAPTOP_USER="neerav" 
LAPTOP_IP="10.41.79.214"  

LOCAL_LOG_DIR="$HOME/helmholtz_minimal_ws/result_logs"
REMOTE_LOG_DIR="~/helmholtz_minimal_ws/result_logs"

echo "Scanning for the newest log file..."

# Find the most recently modified .csv file in the Pi's log directory
NEWEST_FILE=$(ls -t "$LOCAL_LOG_DIR"/*.csv 2>/dev/null | head -n 1)

if [ -z "$NEWEST_FILE" ]; then
    echo "❌ Error: No CSV files found in $LOCAL_LOG_DIR"
    exit 1
fi

FILENAME=$(basename "$NEWEST_FILE")
echo "✅ Found: $FILENAME"
echo "🚀 Transferring to $LAPTOP_USER@$LAPTOP_IP..."

# Execute the secure copy
scp "$NEWEST_FILE" "${LAPTOP_USER}@${LAPTOP_IP}:${REMOTE_LOG_DIR}/"

if [ $? -eq 0 ]; then
    echo "🎉 Transfer complete! Check your laptop's result_logs folder."
else
    echo "❌ Transfer failed. Check your laptop's IP address and SSH settings."
fi
