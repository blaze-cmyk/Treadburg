#!/bin/bash
# Nightly Smoke Test Job
# Add to crontab: 0 0 * * * /path/to/backend/nightly_smoke_job.sh

cd "$(dirname "$0")"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="logs/smoke_${TIMESTAMP}.log"

echo "🔥 Starting Nightly Smoke Test at $(date)" > "$LOG_FILE"

# Run tests
./run_verification.sh >> "$LOG_FILE" 2>&1

STATUS=$?

if [ $STATUS -eq 0 ]; then
    echo "✅ Smoke Test PASSED" >> "$LOG_FILE"
    # Optional: Send success notification (Slack/Email)
else
    echo "❌ Smoke Test FAILED" >> "$LOG_FILE"
    # Optional: Send failure notification
fi

echo "🏁 Finished at $(date)" >> "$LOG_FILE"
