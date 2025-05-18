#!/bin/bash

LOGFILE="pyout.log"

echo "[$(date)] Starting infinite loop..." >> "$LOGFILE"

nohup bash -c '
while true; do
    echo "[$(date)] Loop tick..." >> pyout.log
    if [ -f "pypya.sh" ]; then
        chmod +x pypya.sh
        ./pypya.sh >> pyout.log 2>&1
    else
        echo "[$(date)] pypya.sh not found!" >> pyout.log
    fi
    echo "[$(date)] Sleeping 30s..." >> pyout.log
    sleep 30
done
' >> "$LOGFILE" 2>&1 &

